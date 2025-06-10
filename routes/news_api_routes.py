# backend/routes/news_api_routes.py
# This file now serves to import and expose the news_bp defined in the controller.
# All route definitions for /api/news/* are handled directly within news_controller.py.

from controllers.news_controller import news_bp # Import the Blueprint from the controller

# Rename the imported blueprint to news_api_bp for consistency with app.py's import name
news_api_bp = news_bp
