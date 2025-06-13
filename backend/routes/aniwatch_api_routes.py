# backend/routes/aniwatch_api_routes.py
# This file now serves to import and expose the aniwatch_api_bp defined in the controller.
# All route definitions for /api/aniwatch/* are handled directly within aniwatch_controller.py.

from controllers.aniwatch_controller import aniwatch_api_bp # Import the Blueprint from the controller

# Rename the imported blueprint to aniwatch_api_bp for consistency with app.py's import name
# (Although it's already named that way in the controller for convenience)
aniwatch_api_bp = aniwatch_api_bp
