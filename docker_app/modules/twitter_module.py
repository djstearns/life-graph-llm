import tweepy
import time

class TwitterClient:
    def __init__(self, bearer_token):
        self.client = tweepy.Client(bearer_token)

    def get_tweets(self, handle, count=10):
        """
        Retrieve tweets from a particular handle.

        Parameters:
        - handle (str): The Twitter handle to retrieve tweets from.
        - count (int): The number of tweets to retrieve. Default is 10.

        Returns:
        - list: A list of tweets.
        """
        try:
            user = self.client.get_user(username=handle)
            tweets = self.client.get_users_tweets(id=user.data.id, max_results=count, tweet_fields=["text", "created_at", "geo"])
            return [tweets.data]
            # return [tweet.text for tweet in tweets.data]
            
        except tweepy.TweepyException as e:
            if e.response.status_code == 429:
                print("Rate limit exceeded. Waiting for 5 minutes before retrying...")
                time.sleep(60)  # Wait for 1 minute
                return self.get_tweets(handle, count)  # Retry the request
            else:
                print(f"Error: {e}")
                return []


