# backend/routes/proxy_api_routes.py
from flask import Blueprint
from controllers.proxy_controller import ProxyController

proxy_api_bp = Blueprint('proxy_api', __name__, url_prefix='/api/proxy')

@proxy_api_bp.route('/m3u8', methods=['GET'])
def proxy_m3u8_route():
    """Proxies and rewrites M3U8 playlists."""
    return ProxyController.proxy_m3u8()

@proxy_api_bp.route('/ts', methods=['GET'])
def proxy_ts_route():
    """Proxies video segments (.ts) and encryption keys."""
    return ProxyController.proxy_ts()
