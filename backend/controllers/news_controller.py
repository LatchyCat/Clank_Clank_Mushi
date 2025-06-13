# backend/controllers/news_controller.py (FINALIZED FIX FOR ANN PARSING)
import xml.etree.ElementTree as ET
from services.ann_api_service import ANNAPIService
from flask import current_app, Blueprint, jsonify, request

# Create a Blueprint for news routes with the correct URL prefix
news_bp = Blueprint('news', __name__, url_prefix='/api/news')

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
                # CORRECTED: For search results, the name is typically an attribute of the <title> tag
                for title_elem in root.findall('.//title'):
                    title_id = title_elem.get('id')
                    title_name = title_elem.get('name') # Get name from attribute
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
            elif xml_root_or_error is None: # Corrected from === None to is None
                return {"error": "Failed to fetch title details: Service returned no data."}, 500
            elif ET.iselement(xml_root_or_error):
                root = xml_root_or_error
                # CORRECTED: For direct ID lookup, the item is typically an <anime>, <manga>, or <movie> tag
                # directly under the <ann> root, not a <title> tag.
                title_elem = None
                for child in root:
                    if child.tag in ['anime', 'manga', 'movie', 'ova', 'movie']: # Added 'ova' for completeness
                        title_elem = child
                        break

                if title_elem is None:
                    print(f"DEBUG: NewsController: No item element found for ID {title_id}.")
                    return {"error": f"Title with ID {title_id} not found or no details available."}, 404

                title_details = {
                    "id": title_elem.get('id'),
                    "type": title_elem.get('type'), # Get type directly from the <anime>/<manga>/<movie> tag
                    "genres": [],
                    "themes": [],
                    "staff": [],
                    "episodes": None,
                    "vintage": None,
                    "main_title": None,
                    "alternative_titles": [],
                    "description": None, # Will extract plot summary here
                    "related_titles": [] # Will extract related titles
                }

                # Extract info tags (Main title, Alternative title, Genres, Themes, Episodes, Vintage, Plot Summary)
                for info_elem in title_elem.findall('info'):
                    info_type = info_elem.get('type')
                    if info_type == "Main title":
                        title_details["main_title"] = info_elem.text
                    elif info_type == "Alternative title" and info_elem.text:
                        title_details["alternative_titles"].append(info_elem.text)
                    elif info_type == "Genres" and info_elem.text:
                        title_details["genres"].append(info_elem.text)
                    elif info_type == "Themes" and info_elem.text:
                        title_details["themes"].append(info_elem.text)
                    elif info_type == "Number of episodes" and info_elem.text:
                        try:
                            title_details["episodes"] = int(info_elem.text)
                        except (ValueError, TypeError):
                            title_details["episodes"] = None
                    elif info_type == "Vintage" and info_elem.text:
                        # Vintage can contain multiple dates (e.g., initial run, international release)
                        # For simplicity, taking the first one or concatenating
                        title_details["vintage"] = info_elem.text
                    elif info_type == "Plot Summary" and info_elem.text: # ADDED: Extract description (Plot Summary)
                        title_details["description"] = info_elem.text


                # Extract staff roles
                for staff_elem in title_elem.findall('staff'):
                    task = staff_elem.find('task').text if staff_elem.find('task') is not None else "Unknown Task"
                    person = staff_elem.find('person').text if staff_elem.find('person') is not None else "Unknown Person"
                    person_id = staff_elem.find('person').get('id') if staff_elem.find('person') is not None else None
                    title_details["staff"].append({
                        "task": task,
                        "person": person,
                        "person_id": person_id
                    })

                # Extract related titles (e.g., prequel, sequel, adapted from)
                # ANN uses tags like <related-prev>, <related-next>, <related-other>
                for related_elem in title_elem.findall('related-prev') + \
                                    title_elem.findall('related-next') + \
                                    title_elem.findall('related-other') + \
                                    title_elem.findall('related'): # Catch any generic 'related' tag
                    relation = related_elem.get('rel')
                    related_id = related_elem.get('id')

                    # Some related tags might have a 'type' or 'name' attribute, or a child 'title' tag.
                    # We'll prioritize attributes if available, then check for a child 'title'
                    related_type = related_elem.get('type')
                    related_name = related_elem.get('name')

                    # If name is not directly on the <related-*> tag, check for a child <title>
                    if not related_name:
                        child_title_elem = related_elem.find('title')
                        if child_title_elem is not None:
                            related_name = child_title_elem.text

                    if relation and related_id:
                        title_details["related_titles"].append({
                            "relation": relation,
                            "id": related_id,
                            "type": related_type, # May be None if not present
                            "name": related_name # May be None if not present
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
            xml_root_or_error = self.ann_service.get_staff_ann(str(staff_id))

            if isinstance(xml_root_or_error, dict) and "error" in xml_root_or_error:
                print(f"DEBUG: NewsController: Error from service: {xml_root_or_error.get('error')}")
                return xml_root_or_error, xml_root_or_error.get('status_code', 500)
            elif xml_root_or_error is None:
                return {"error": "Failed to fetch staff details: Service returned no data."}, 500
            elif ET.iselement(xml_root_or_error):
                root = xml_root_or_error
                person_elem = root.find('person')
                if person_elem is None:
                    print(f"DEBUG: NewsController: No person element found for ID {staff_id}.")
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
