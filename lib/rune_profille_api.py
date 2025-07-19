import json
from typing import Any, Dict, Optional

import requests


class RuneProfileApiError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


class RuneProfileAPI:
    def __init__(self, base_url: str):
        """
        Initialize the RuneProfile API client

        Args:
            base_url: The base URL for the API (e.g., "https://api.runeprofile.com")
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a request to the API and handle errors"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.get(url, params=params)
            data = response.json()

            if response.ok:
                return data

            # Handle API errors
            if isinstance(data, dict) and "code" in data and "message" in data:
                raise RuneProfileApiError(data["code"], data["message"])
            else:
                raise RuneProfileApiError(
                    "UnexpectedError", "Something unexpected went wrong"
                )

        except requests.exceptions.RequestException as e:
            raise RuneProfileApiError("NetworkError", f"Network error: {str(e)}")
        except json.JSONDecodeError:
            raise RuneProfileApiError("ParseError", "Failed to parse response")

    def get_profile(self, username: str) -> Dict[str, Any]:
        """Get player profile data"""
        return self._make_request(f"/profiles/{username}")

    def search_profiles(self, query: str) -> Dict[str, Any]:
        """Search for profiles"""
        return self._make_request("/profiles", params={"q": query})

    def get_clan_members(self, clan_name: str, page: int = 1) -> Dict[str, Any]:
        """Get clan members"""
        return self._make_request(f"/clans/{clan_name}", params={"page": str(page)})
