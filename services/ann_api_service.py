# backend/services/ann_api_service.py (UPDATED)
import requests
import xml.etree.ElementTree as ET
import json

class ANNAPIService:
    API_BASE_URL = "https://www.animenewsnetwork.com/encyclopedia/api.xml"
    REPORTS_API_URL = "https://www.animenewsnetwork.com/encyclopedia/reports.xml"
    USER_AGENT = "ClankClankMushi/1.0 (https://github.com/your-repo-link; your-email@example.com)" # Replace with your repo and email

    def _make_request(self, base_url, params=None):
        url = base_url
        headers = {
            "User-Agent": self.USER_AGENT,
            "Accept": "application/xml"
        }

        print(f"DEBUG: ANNAPIService: Making request to: {url} with params: {params}")
        try:
            # Increased timeout to 30 seconds
            response = requests.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            print("\n--- Raw ANN API Response Content for Debugging ---")
            raw_content = response.content.decode('utf-8', errors='ignore')
            print(raw_content)
            print("--- End Raw ANN API Response Content ---\n")

            try:
                root = ET.fromstring(raw_content)
                # Check for an 'ann' root with a 'warning' child
                warning_elem = root.find('warning')
                if warning_elem is not None:
                    # Return a structured error if a warning is received from API
                    return {"error": warning_elem.text, "status_code": 404} # Use 404 for ignored parameters

                return root # Return the root if no warning

            except ET.ParseError as xml_e:
                print(f"DEBUG: ANNAPIService: XML parsing failed: {xml_e}")
                # Return a structured error for parsing issues
                return {"error": f"Failed to parse XML response from ANN API: {xml_e}", "raw_response": raw_content, "status_code": 500}

        except requests.exceptions.HTTPError as e:
            print(f"DEBUG: ANNAPIService: HTTP error occurred: {e.response.status_code} - {e.response.text}")
            return {"error": f"HTTP error from ANN API: {e.response.status_code}", "details": e.response.text, "status_code": e.response.status_code}, 500
        except requests.exceptions.ConnectionError as e:
            print(f"DEBUG: ANNAPIService: Connection error occurred: {e}")
            return {"error": f"Could not connect to ANN API: {e}", "status_code": 503}
        except requests.exceptions.Timeout as e:
            print(f"DEBUG: ANNAPIService: Request timed out: {e}")
            return {"error": "ANN API request timed out.", "status_code": 504}
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: ANNAPIService: An unexpected request error occurred: {e}")
            return {"error": f"An unexpected error occurred with ANN API request: {e}", "status_code": 500}

    def search_news_ann(self, query: str):
        params = {"title": f"~{query}"} # Use '~' for searching
        return self._make_request(base_url=self.API_BASE_URL, params=params)

    def get_news_title_ann(self, item_id: str):
        # Use 'title=ID' for direct title lookup
        params = {"title": item_id}
        return self._make_request(base_url=self.API_BASE_URL, params=params)

    def get_staff_ann(self, staff_id: str):
        # We know 'person=ID' is ignored. Re-evaluate this.
        # For now, it will return an error due to the warning in _make_request.
        params = {"person": staff_id}
        return self._make_request(base_url=self.API_BASE_URL, params=params)

    def get_recent_items(self, report_id: int = 155, item_type: str = None, limit: int = None, skip: int = 0):
        params = {"id": report_id}
        if item_type:
            params['type'] = item_type
        if limit:
            params['nlist'] = limit
        if skip:
            params['nskip'] = skip

        return self._make_request(base_url=self.REPORTS_API_URL, params=params)
