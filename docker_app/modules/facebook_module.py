import requests
import time
from typing import List, Dict, Optional

class FacebookClient:
    """
    Minimal Facebook Graph API client for fetching /me feed.
    Usage:
      fb = FacebookClient(access_token)
      feed_items = fb.get_feed(limit=5)
      messages = fb.get_messages(limit=5)
    """
    def __init__(self, access_token: str, api_version: str = "v24.0"):
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{self.api_version}/me"

    def _request(self, params: Dict = None, full_url: str = None, retry: bool = True) -> Optional[Dict]:
        try:
            if full_url:
                resp = requests.get(full_url, timeout=10)
            else:
                resp = requests.get(self.base_url, params=params, timeout=10)
            if resp.status_code == 429:
                # rate limited: wait 5 minutes then retry once
                print("Rate limit (429) from Facebook API, waiting 5 minutes before retry...")
                time.sleep(300)
                if retry:
                    return self._request(params=params, full_url=full_url, retry=False)
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            print(f"Facebook request error: {e}")
            return None

    def get_feed(self, fields: str = "id,name,feed{message,created_time,event,description,coordinates,story,dynamic_posts{message,title}}", limit: int = 10) -> List[Dict]:
        """
        Fetch the /me feed. Follows paging['next'] URLs until `limit` items gathered
        or no further pages exist. Returns a list of feed item dicts (empty list on error).
        """
        params = {
            "fields": fields,
            "access_token": self.access_token,
            "limit": min(limit, 100)  # request a reasonable per-page size
        }

        collected: List[Dict] = []
        data = self._request(params=params)
        if not data:
            return []

        # initial page may nest feed under 'feed' or be a direct data page
        def extract_items(resp_json: Dict) -> List[Dict]:
            if not resp_json:
                return []
            if "feed" in resp_json and isinstance(resp_json["feed"], dict):
                return resp_json["feed"].get("data", []) or []
            return resp_json.get("data", []) or []

        items = extract_items(data)
        collected.extend(items)

        # Find next page url if present
        next_url = None
        # Try to get paging from either top-level feed or top-level response
        if "feed" in data and isinstance(data["feed"], dict):
            next_url = data["feed"].get("paging", {}).get("next")
        else:
            next_url = data.get("paging", {}).get("next")

        # Follow paging.next until we have enough items or no next link
        pages_followed = 0
        MAX_PAGES = 50
        while len(collected) < limit and next_url and pages_followed < MAX_PAGES:
            pages_followed += 1
            page = self._request(full_url=next_url)
            if not page:
                break
            page_items = extract_items(page)
            collected.extend(page_items)

            # update next_url from this page
            next_url = page.get("paging", {}).get("next")
        
        # Return at most `limit` items
        return collected[:limit] if isinstance(collected, list) else []

    def get_messages(self, limit: int = 10) -> List[Dict[str, Optional[str]]]:
        """
        Convenience: return a list of dicts with 'message' and 'created_time' from feed items.
        """
        items = self.get_feed(limit=limit)
        messages: List[Dict[str, Optional[str]]] = []
        for it in items:
            created_time = it.get("created_time")
            # prefer explicit message, fallback to story or description
            msg = it.get("message") or it.get("story") or it.get("description")
            if msg:
                messages.append({
                    "message": msg,
                    "created_time": created_time
                })
        return messages
