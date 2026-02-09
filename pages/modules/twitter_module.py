import requests
from typing import Optional, Dict, Any

class TwitterAPI:
    """
    Simple Python module for interacting with Twitter API v2 using a Bearer Token.
    Does not require tweepy.
    """

    BASE_URL = "https://api.x.com/2"

    def __init__(self, bearer_token: str):
        if not bearer_token:
            raise ValueError("A valid Bearer Token must be provided.")
        self.bearer_token = bearer_token
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code != 200:
            raise Exception(f"Twitter API error {response.status_code}: {response.text}")

        return response.json()

    def get_user_by_username(self, username: str) -> Dict[str, Any]:
        """Fetch user details from a username."""
        endpoint = f"/users/by/username/{username}"
        return self._get(endpoint)

    def get_user_tweets(self, user_id: str, max_results: int = 10) -> Dict[str, Any]:
        """Fetch recent tweets from user by user ID."""
        endpoint = f"/users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics"
        }
        return self._get(endpoint, params=params)

    def search_tweets(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search for tweets using Twitter API v2 search endpoint."""
        endpoint = "/tweets/search/recent"
        params = {
            "query": query,
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics"
        }
        return self._get(endpoint, params=params)


# Example usage (remove or wrap in `if __name__ == "__main__":` if needed):
# api = TwitterAPI("YOUR_BEARER_TOKEN")
# user = api.get_user_by_username("jack")
# tweets = api.get_user_tweets(user["data"]["id"], max_results=5)
# print(tweets)
