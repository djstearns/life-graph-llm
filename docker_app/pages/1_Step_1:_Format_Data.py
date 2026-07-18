import streamlit as st
import json
import boto3
import numpy as np
import time
import re
import os
import requests
from utils.session_auth import require_login
from utils.llm import Llm
from config_file import Config
import streamlit.components.v1 as components
from modules.twitter_module import TwitterAPI # Import the Twitter client
from modules.facebook_module import FacebookClient  # Import the Facebook client

css = '''
<style>
    [data-testid="stMain"] {
        max-width: none;
        overflow: auto;
    }
    section[data-testid="stMain"] {
        display: contents;
        overflow: auto;
    }
    [data-testid="stAppViewContainer"] {
        overflow: auto;
        
    }
</style>
'''
st.markdown(css, unsafe_allow_html=True)

# st.markdown("""
#         <script src="https://apis.google.com/js/api.js"></script>
#         <script type="text/javascript" >
#         // initTokenClient() initializes a new token client with your
#         // web app's client ID and the scope you need access to

#         const client = google.accounts.oauth2.initTokenClient({
#         client_id: 'YOUR_CLIENT',
#         scope: 'https://www.googleapis.com/auth/calendar.readonly',
        
#         // callback function to handle the token response
#         callback: (tokenResponse) => {
#             if (tokenResponse && tokenResponse.access_token) { 
#             gapi.client.setApiKey('YOUR_API_KEY_HERE');
#             gapi.client.load('calendar', 'v3', listUpcomingEvents);
#             }
#         },
#         });

#         function listUpcomingEvents() {
#         gapi.client.calendar.events.list();
#         }

#         listUpcomingEvents();
#         </script>
#         """, unsafe_allow_html=True)


if 'json_suggestion' in st.session_state:
    json_suggestion = st.session_state["json_suggestion"]
    # st.write(json_suggestion)
else:
    st.session_state["json_suggestion"] = None
    json_suggestion = None

# # When there is an input text to process
def run_llm(input_sent, llm):
    if input_sent:
        # Invoke the Bedrock foundation model
        if st.session_state.get("auth_method", "AWS IAM Keys") == "OpenAI API Key":
            llm = Llm(Config.BEDROCK_REGION, openai_api_key=st.session_state.get("openai_api_key", None))
            response = llm.invoke_openai(input_sent)
        else:
            llm = Llm(Config.BEDROCK_REGION, aws_secret_access_key=st.session_state.get("aws_secret_access_key", None), aws_access_key_id=st.session_state.get("aws_access_key_id", None))
            response = llm.invoke(input_sent)

        # Transform response to json
        if st.session_state.get("auth_method", "AWS IAM Keys") == "OpenAI API Key":
            print(response.text)
            responses = json.loads(response.text)
            print(responses)
            # response.text.choices[0].message.content
            json_response = responses['choices'][0]['message']['content']
            pretty_json_output = json.dumps(json_response, indent=2)
            st.session_state.llm_output = json_response
        else:
            json_response = json.loads(response.get("body").read())
               # Format response and print it in the console
            pretty_json_output = json.dumps(json_response, indent=2)
            
            st.session_state.llm_output = json_response['content'][0]['text']

        print("API response: ", pretty_json_output)
        # Write response on Streamlit web interface
        st.write("**Foundation model output** \n\n", json_response)
        session_state = st.session_state
       
        # Regular expression to match content between triple backticks
        # pattern = r"```(.*?)```"
        # Find all matches and return them as a list
        #code_blocks = re.findall(pattern, json_response['completion'], re.DOTALL)
        return
#         # if 'key' not in st.session_state:
          
def keep_values():
    for key in st.session_state:
        if ':' not in key:
            st.session_state[key] = st.session_state[key]
keep_values()

platform_options = ["Facebook","Twitter", "Web"]

# Add title on the page
st.title("Step 1b: Create your new Life Graph JSON Data")

# ensure session_state defaults for persistent inputs
if 'aws_access_key_id' not in st.session_state:
    st.session_state['aws_access_key_id'] = ""
if 'fb_access_token' not in st.session_state:
    st.session_state['fb_access_token'] = ""
if 'bearer_token' not in st.session_state:
    st.session_state['bearer_token'] = ""
if 'twitter_handle' not in st.session_state:
    st.session_state['twitter_handle'] = ""
if 'num_tweets' not in st.session_state:
    st.session_state['num_tweets'] = 10
if 'fb_num_posts' not in st.session_state:
    st.session_state['fb_num_posts'] = 10
if 'input_area' not in st.session_state:
    st.session_state['input_area'] = st.session_state.get('json_suggestion') or ""
if 'web_url' not in st.session_state:
    st.session_state['web_url'] = ""
if 'llm_output' not in st.session_state:
    st.session_state['llm_output'] = ""
if 'tweets' not in st.session_state:
    st.session_state['tweets'] = []
if 'facebook_feed' not in st.session_state:
    st.session_state['facebook_feed'] = []
if 'web_content' not in st.session_state:
    st.session_state['web_content'] = ""
if 'platform' not in st.session_state:
    st.session_state['platform'] = platform_options[2]


with st.sidebar:
    st.sidebar.header("Step 1a: Get your data")

    # Platform selector: show only the relevant controls (persisted)
     # Platform selector: show only the relevant controls (persisted)
    platform = st.sidebar.selectbox("Platform", options=platform_options, key='platform', on_change=keep_values)
    
    if platform == "Twitter":
        # Add Twitter form in the sidebar
        st.sidebar.subheader("Fetch Tweets")
        bearer_token = st.sidebar.text_input("Bearer Token", key='bearer_token', on_change=keep_values, type="password")
        twitter_handle = st.sidebar.text_input("Twitter Handle", key='twitter_handle', on_change=keep_values, )
        num_tweets = st.sidebar.number_input("Number of Tweets", min_value=1, max_value=100, value=st.session_state['num_tweets'], key='num_tweets', on_change=keep_values)
        fetch_tweets_button = st.sidebar.button("Fetch Tweets")

        if fetch_tweets_button and st.session_state['twitter_handle']:
            try:
                # Example usage (remove or wrap in `if __name__ == "__main__":` if needed):
                api = TwitterAPI(st.session_state['bearer_token'])
                user = api.get_user_by_username(st.session_state['twitter_handle'])
                tweets = api.get_user_tweets(user["data"]["id"], max_results=st.session_state['num_tweets'])
                # print(tweets)
                # Create an instance of the TwitterClient using persisted token
                ###### OLD #####
                # twitter_client = TwitterClient(st.session_state['bearer_token'])
                # Fetch the tweets
                # tweets = twitter_client.get_tweets(st.session_state['twitter_handle'], st.session_state['num_tweets'])
                # Check for empty result (graceful failure)
                if not tweets:
                    st.sidebar.error("No tweets returned. This may indicate an expired or invalid bearer token, a private account, or no available tweets.")
                    st.sidebar.info("Try refreshing your token, verifying the handle, or checking account privacy settings.")
                    st.session_state["tweets"] = []
                    st.session_state["input_area"] = ""
                else:
                    # Save to session_state and also populate the shared input_area
                    st.session_state["tweets"] = tweets
                    st.session_state["bearer_token"] = bearer_token
                    st.session_state["twitter_handle"] = twitter_handle
                    st.session_state["num_tweets"] = num_tweets
                    try:
                        st.session_state["input_area"] = json.dumps(tweets, indent=2)
                    except Exception:
                        st.session_state["input_area"] = str(tweets)
            except Exception as e:
                st.sidebar.error(f"Failed to fetch tweets: {e}")
                st.sidebar.warning("This failure is often caused by an expired/invalid bearer token or network/permission issues.")
                st.session_state["tweets"] = []
                st.session_state["input_area"] = ""
            

    elif platform == "Facebook":
        # Facebook controls (shown only when platform == "Facebook")
        st.sidebar.subheader("Fetch Facebook Feed")
        fb_access_token = st.sidebar.text_input("Facebook Access Token", key='fb_access_token', on_change=keep_values, type='password')
        fb_num_posts = st.sidebar.number_input("Number of Posts", min_value=1, max_value=10000, key='fb_num_posts', on_change=keep_values)
        fetch_facebook_button = st.sidebar.button("Fetch Facebook Feed")

        if fetch_facebook_button and st.session_state['fb_access_token']:
            try:
                fb_client = FacebookClient(st.session_state['fb_access_token'])
                fb_messages = fb_client.get_messages(limit=st.session_state['fb_num_posts'])
                # Check for empty result (graceful failure)
                if not fb_messages:
                    st.sidebar.error("No Facebook feed items returned. This may indicate an expired/invalid access token or insufficient permissions.")
                    st.sidebar.info("Try refreshing the access token, ensuring the app has the required permissions, or reducing the number of posts requested.")
                    st.session_state["facebook_feed"] = []
                    st.session_state["input_area"] = ""
                else:
                    # Insert fetched facebook content into the shared form text_area
                    st.session_state.fbtoken = fb_access_token
                    try:
                        st.session_state["input_area"] = json.dumps(fb_messages, indent=2)
                    except Exception:
                        st.session_state["input_area"] = str(fb_messages)
            except Exception as e:
                st.sidebar.error(f"Failed to fetch Facebook feed: {e}")
                st.sidebar.warning("This failure is often caused by an expired/invalid access token, missing permissions, or network issues.")
                st.session_state["facebook_feed"] = []
                st.session_state["input_area"] = ""
            

    elif platform == "Web":
        st.sidebar.subheader("Fetch web Content:")
        web_url = st.sidebar.text_input("Web URL", key='web_url', on_change=keep_values)
        fetch_web_button = st.sidebar.button("Fetch web Content")
        st.sidebar.header('Decide your LLM')
        # Dropdown to select authentication method
          # Dropdown to select authentication method
        auth_method = st.sidebar.selectbox(
            "Choose authentication method for LLM:",
            ["AWS IAM Keys", "OpenAI API Key"], key="auth_method"
        )
        

        if fetch_web_button and st.session_state['web_url']:
            try:
                response = requests.get(web_url)
                if response.status_code == 200:
                    web_content = response.text
                    st.session_state["web_content"] = web_content
                    # put content into shared input area too
                    st.session_state["input_area"] = web_content
                else:
                    st.sidebar.error("Failed to fetch web content")
            except Exception as e:
                st.sidebar.error(f"Failed to fetch web content: {e}")
                st.session_state["web_content"] = ""
                st.session_state["input_area"] = ""
    

    

st.header("How to use this page:")
st.write("This Page has two sections: The first is your current draft of Current Json Data, the second is a form that generates a json string that you can use to create your life graph. The third section is a form that fetches content from a twitter handle. You can use the content to generate a json string for your life graph. " \
" Consider using RSS feeds: https://news.yahoo.com/rss/us. A listing is here: https://about.fb.com/wp-content/uploads/2016/05/rss-urls-1.pdf" \
" Blogs: https://wanderingearl.com/feed/ , you may be able to add'/feed' to the end of a wordpress blog")


# Ask user for input text
with st.form("my_form"):
    st.write("This form will generate json you can use in this web session to create your life graph. The first prompt will give you an annonymized example with no social data, the latter example requires you to gather data from a web source: ")
    instr_str = """
    Create a json string with 10 events of a typical American using single dates as well as range of dates with comments similar to this: {"birthdate":"1987-08-13", "data":[{"date": "2024-09-17", "comment": "B"}, {"date": "2024-09-16", "comment": "A"}, {"range":["1987-08-15","1988-01-01"], "comment":"birth"}]} 
    """
    st.code(instr_str,wrap_lines=True)
    "==== OR ===="
    try:
        with open(st.session_state.get('selected_prompt_path'), 'r') as fh:
            data = fh.read()
            if 'selected_prompt_path' in st.session_state:
                st.code(data, language='json',wrap_lines=True)
       
    except Exception as e:
        st.write(f'Unable to preview file: {e}')

   
    input_pre = st.text_area("Input: Prefix Sentence to LLM", value=st.session_state.get('input_pre', ""), key="preinput_area")
    st.session_state['input_pre'] = input_pre
    # bind the text area to a persistent session_state key so it survives page switches
    input_val = st.text_area("Automated Input: Social Media Event Data", value=st.session_state.get('input_area', json_suggestion), key="input_area")

    # Show input fields based on selection
    if auth_method == "AWS IAM Keys": 
        aws_access_key_id = st.text_input("Provide your IAM User Access Key ID to enable LLM calls.", key="aws_access_key_id",type="password")
        aws_secret_access_key = st.text_input("Provide your IAM User Secret Access Key to enable LLM calls.", key="aws_secret_access_key",type="password")   
        
    elif auth_method == "OpenAI API Key":
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        st.session_state["openai_api_key"] = openai_api_key

    # st.text_input("Provide your IAM User Access Key ID to enable LLM calls.", key="aws_access_key_id",type="password")
    # st.text_input("Provide your IAM User Secret Access Key to enable LLM calls.", key="aws_secret_access_key",type="password")   

    # Submit: call LLM using the value currently in session_state   
    submitted = st.form_submit_button(label="Submit", type="secondary")
    if submitted:
        full_str = input_pre + "\n" + st.session_state.get('input_area', "")
        llm = Llm(Config.BEDROCK_REGION, st.session_state.get("aws_access_key_id", None),
          st.session_state.get("aws_secret_access_key", None))
        run_llm(full_str, llm)

    # Render LLM output after possible run_llm() call so it appears on first submit
    llm_output = st.session_state.get('llm_output', "")
    st.text_area("LLM Output", value=llm_output, height=300)

if 'tweets' in st.session_state:
    st.write(st.session_state["tweets"])

# show facebook feed if fetched
if 'facebook_feed' in st.session_state:
    st.write(st.session_state["facebook_feed"])

# require_login()
