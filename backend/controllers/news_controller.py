# backend/controllers/news_controller.py (FURTHER UPDATED)
import xml.etree.ElementTree as ET
from services.ann_api_service import ANNAPIService
from flask import current_app, Blueprint, jsonify, request

# Create a Blueprint for news routes
news_bp = Blueprint('news', __name__)

class NewsController:
    """
    Controller for handling anime news and encyclopedia data from the ANN API.
    It calls the ANNAPIService to fetch raw data (expected XML) and then
    parses that XML into a structured dictionary/list format for the frontend.
    """
    def __init__(self):
        self.ann_service = ANNAPIService()

    def get_recent_news_articles(self, limit=10):
        """
        Fetches recent encyclopedia items (e.g., new anime titles) from ANN API via reports.
        Parses the XML response into a structured list.
        """
        print(f"DEBUG: NewsController: Fetching recent items (report 155, limit={limit})...")
        try:
            # Report ID 155 is specifically for recent anime items, so 'item_type="anime"'
            # is not a necessary parameter for reports.xml and can be removed.
            xml_root_or_error = self.ann_service.get_recent_items(report_id=155, limit=limit)

            # Handle errors returned from service (which are now dicts with 'error' and 'status_code')
            if isinstance(xml_root_or_error, dict) and "error" in xml_root_or_error:
                print(f"DEBUG: NewsController: Error from service: {xml_root_or_error.get('error')}")
                return xml_root_or_error, xml_root_or_error.get('status_code', 500)
            elif xml_root_or_error is None:
                print(f"DEBUG: NewsController: Failed to fetch recent items: Service returned no data (None).")
                return {"error": "Failed to fetch recent items: Service returned no data."}, 500
            elif ET.iselement(xml_root_or_error): # Check if it's an ElementTree root
                root = xml_root_or_error
                formatted_items = []

                # ANN reports.xml structure: <report><item><id>...</id><name>...</name>...</item></report>
                # The 'id', 'name', 'type', 'gid', 'precision', 'vintage' are child elements of <item>
                # We need to use .find("tag_name").text to get their values.
                for item_elem in root.findall('.//item'):
                    # Extract data from child elements, checking if the child element exists before accessing .text
                    item_data = {
                        "id": item_elem.find("id").text if item_elem.find("id") is not None else None,
                        "gid": item_elem.find("gid").text if item_elem.find("gid") is not None else None,
                        "type": item_elem.find("type").text if item_elem.find("type") is not None else None,
                        "name": item_elem.find("name").text if item_elem.find("name") is not None else None,
                        "precision": item_elem.find("precision").text if item_elem.find("precision") is not None else None,
                        "vintage": item_elem.find("vintage").text if item_elem.find("vintage") is not None else None
                    }

                    # Validation step
                    if item_data.get("id") and item_data.get("name"):
                        formatted_items.append(item_data)
                    else:
                        current_app.logger.warning(f"NewsController: Skipping item due to missing ID or Name: {item_data}")
                return formatted_items, 200
            else:
                print(f"DEBUG: NewsController: Unexpected response type from service: {type(xml_root_or_error)}")
                return {"error": "Unexpected data format from ANN API service."}, 500

        except Exception as e:
            print(f"DEBUG: NewsController: An unexpected error occurred in get_recent_news_articles: {e}")
            return {"error": f"An unexpected error occurred: {e}"}, 500

    def search_ann_titles(self, query: str):
        """
        Searches ANN encyclopedia for titles matching a query.
        """
        print(f"DEBUG: NewsController: Searching ANN titles for query: '{query}'")
        try:
            xml_root_or_error = self.ann_service.search_news_ann(query)

            if isinstance(xml_root_or_error, dict) and "error" in xml_root_or_error:
                print(f"DEBUG: NewsController: Error from service: {xml_root_or_error.get('error')}")
                return xml_root_or_error, xml_root_or_error.get('status_code', 500)
            elif xml_root_or_error is None:
                return {"error": "Failed to search titles: Service returned no data."}, 500
            elif ET.iselement(xml_root_or_error):
                root = xml_root_or_error
                titles = []
                # Find all 'title' elements directly under the 'ann' root
                for title_elem in root.findall('.//title'):
                    title_id = title_elem.get('id')
                    title_name = title_elem.find('info[@type="Main title"]').text if title_elem.find('info[@type="Main title"]') is not None else None
                    title_type = title_elem.get('type') # e.g., manga, anime, OAV, movie

                    if title_id and title_name:
                        titles.append({
                            "id": title_id,
                            "name": title_name,
                            "type": title_type
                        })
                print(f"DEBUG: NewsController: Found {len(titles)} titles for query '{query}'.")
                return titles, 200
            else:
                return {"error": "Unexpected data format from ANN API service."}, 500

        except Exception as e:
            print(f"DEBUG: NewsController: An error occurred in search_ann_titles: {e}")
            return {"error": f"An unexpected error occurred during search: {e}"}, 500


    def get_ann_title_details(self, title_id: int):
        """
        Fetches detailed information for a specific ANN title ID.
        """
        print(f"DEBUG: NewsController: Fetching details for title ID: {title_id}")
        try:
            xml_root_or_error = self.ann_service.get_news_title_ann(str(title_id))

            if isinstance(xml_root_or_error, dict) and "error" in xml_root_or_error:
                print(f"DEBUG: NewsController: Error from service: {xml_root_or_error.get('error')}")
                return xml_root_or_error, xml_root_or_error.get('status_code', 500)
            elif xml_root_or_error is None:
                return {"error": "Failed to fetch title details: Service returned no data."}, 500
            elif ET.iselement(xml_root_or_error):
                root = xml_root_or_error
                title_elem = root.find('title') # The root is <ann>, we look for <title> inside
                if title_elem is None:
                    print(f"DEBUG: NewsController: No title element found for ID {title_id}.")
                    return {"error": f"Title with ID {title_id} not found or no details available."}, 404

                title_details = {
                    "id": title_elem.get('id'),
                    "type": title_elem.get('type'),
                    "genres": [],
                    "themes": [],
                    "staff": [],
                    "episodes": None,
                    "vintage": None,
                    "main_title": None,
                    "alternative_titles": []
                }

                # Extract main title and alternative titles
                for info_elem in title_elem.findall('info'):
                    info_type = info_elem.get('type')
                    if info_type == "Main title":
                        title_details["main_title"] = info_elem.text
                    elif info_type == "Alternative title":
                        title_details["alternative_titles"].append(info_elem.text)
                    elif info_type == "Genres" and info_elem.text:
                        title_details["genres"].append(info_elem.text)
                    elif info_type == "Themes" and info_elem.text:
                        title_details["themes"].append(info_elem.text)
                    elif info_type == "Number of episodes" and info_elem.text:
                        try:
                            title_details["episodes"] = int(info_elem.text)
                        except (ValueError, TypeError):
                            title_details["episodes"] = None # Keep as None if conversion fails
                    elif info_type == "Vintage" and info_elem.text:
                        title_details["vintage"] = info_elem.text


                # Extract staff roles
                for staff_elem in title_elem.findall('staff'):
                    task = staff_elem.find('task').text if staff_elem.find('task') is not None else "Unknown Task"
                    person = staff_elem.find('person').text if staff_elem.find('person') is not None else "Unknown Person"
                    staff_id = staff_elem.find('person').get('id') if staff_elem.find('person') is not None else None
                    title_details["staff"].append({
                        "task": task,
                        "person": person,
                        "person_id": staff_id
                    })

                print(f"DEBUG: NewsController: Successfully parsed details for title ID {title_id}.")
                return title_details, 200
            else:
                return {"error": "Unexpected data format from ANN API service."}, 500

        except Exception as e:
            print(f"DEBUG: NewsController: An error occurred in get_ann_title_details: {e}")
            return {"error": f"An error occurred while getting title details: {e}"}, 500

    def get_ann_staff_details(self, staff_id: int):
        """
        Fetches detailed information for a specific ANN staff ID.
        ANN API's /api.xml endpoint does not directly support 'person=ID' lookup reliably,
        as it often redirects to search results or requires a different approach for staff.
        This implementation will attempt a direct lookup, but may need refinement
        if the ANN API behavior is inconsistent.
        """
        print(f"DEBUG: NewsController: Fetching details for staff ID: {staff_id}")
        try:
            # The ANN API's direct 'person=ID' parameter often behaves like a search
            # or doesn't return a direct person entry. It expects the ID in the 'person' attribute
            # of a <person> tag, not as a direct query parameter.
            # We are calling get_staff_ann which uses params={"person": staff_id}.
            # The previous logs indicated this might not be working as expected.
            # Let's verify the `get_staff_ann` behavior in `ANNAPIService`.
            # ANNAPIService.get_staff_ann currently uses params={"person": staff_id}
            # which for /api.xml might not work as expected for direct lookup.
            # The API documentation implies direct person lookups are less straightforward than titles.
            # For this example, we'll proceed assuming it *might* return some relevant XML,
            # but this is a known tricky part of the ANN API.
            xml_root_or_error = self.ann_service.get_staff_ann(str(staff_id))

            if isinstance(xml_root_or_error, dict) and "error" in xml_root_or_error:
                print(f"DEBUG: NewsController: Error from service: {xml_root_or_error.get('error')}")
                return xml_root_or_error, xml_root_or_error.get('status_code', 500)
            elif xml_root_or_error is None:
                return {"error": "Failed to fetch staff details: Service returned no data."}, 500
            elif ET.iselement(xml_root_or_error):
                root = xml_root_or_error
                # ANN API structure for staff details can be complex.
                # Assuming a direct 'person' element under 'ann' if found.
                person_elem = root.find('person')
                if person_elem is None:
                    print(f"DEBUG: NewsController: No person element found for ID {staff_id}.")
                    # If it's a search result, it might contain 'person' elements under 'ann'.
                    # For now, let's assume direct lookup is expected.
                    return {"error": f"Staff with ID {staff_id} not found or no details available."}, 404

                staff_data = {
                    "id": person_elem.get('id'),
                    "name": person_elem.get('name'), # 'name' is an attribute of person
                    "birthdate": None,
                    "deathdate": None,
                    "gender": None,
                    "roles": []
                }

                # Extract info tags
                for info_elem in person_elem.findall('info'):
                    info_type = info_elem.get('type')
                    if info_type == "Birthdate":
                        staff_data["birthdate"] = info_elem.text
                    elif info_type == "Deathdate":
                        staff_data["deathdate"] = info_elem.text
                    elif info_type == "Gender":
                        staff_data["gender"] = info_elem.text

                # Extract staff roles (tasks)
                for task_elem in person_elem.findall('task'):
                    role = task_elem.text
                    title_id = task_elem.get('id') # Associated title ID
                    staff_data["roles"].append({
                        "role": role,
                        "title_id": title_id
                    })

                # Helper to convert single-item lists to single values for specific fields
                def unwrap_single_list_item(v):
                    return v[0] if isinstance(v, list) and len(v) == 1 else v

                # Apply unwrapping for fields that should be single values
                staff_data = {k: unwrap_single_list_item(v) for k, v in staff_data.items() if not isinstance(v, list) or v}

                print(f"DEBUG: NewsController: Successfully parsed details for staff ID {staff_id}.")
                return staff_data, 200

            else:
                return {"error": "Unexpected data format from ANN API service."}, 500

        except Exception as e:
            print(f"DEBUG: NewsController: An error occurred in get_ann_staff_details: {e}")
            return {"error": f"An error occurred while getting staff details: {e}"}, 500

# Initialize the controller
news_controller = NewsController()

# Define Flask routes using the Blueprint
@news_bp.route('/ann/search', methods=['GET'])
def ann_search_titles_route():
    query = request.args.get('q')
    if not query:
        return jsonify({"error": "Query parameter 'q' is required."}), 400

    titles, status_code = news_controller.search_ann_titles(query)
    return jsonify(titles), status_code

@news_bp.route('/ann/title/<int:title_id>', methods=['GET'])
def ann_get_title_details_route(title_id):
    details, status_code = news_controller.get_ann_title_details(title_id)
    return jsonify(details), status_code

@news_bp.route('/ann/staff/<int:staff_id>', methods=['GET'])
def ann_get_staff_details_route(staff_id):
    details, status_code = news_controller.get_ann_staff_details(staff_id)
    return jsonify(details), status_code

@news_bp.route('/ann/recent', methods=['GET'])
def ann_get_recent_news_articles_route():
    limit = request.args.get('limit', 10, type=int)
    articles, status_code = news_controller.get_recent_news_articles(limit=limit)
    return jsonify(articles), status_code
