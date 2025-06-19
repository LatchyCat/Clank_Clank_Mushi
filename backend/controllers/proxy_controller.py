# backend/controllers/proxy_controller.py
import requests
import logging
import json
import re
from flask import Response, request
from urllib.parse import urlparse, urljoin, quote

# Using the globally initialized scraper for consistency
from globals import global_anime_api_service

logger = logging.getLogger(__name__)

class ProxyController:
    """
    Handles proxying of M3U8 playlists and their corresponding TS segments/keys.
    This functionality is now integrated directly into the Mushi backend.
    """

    @staticmethod
    def proxy_m3u8():
        """
        Fetches an M3U8 playlist, rewrites its internal URLs to point to our proxy,
        and returns the modified playlist.
        """
        target_url = request.args.get('url')
        if not target_url:
            return Response("URL parameter is required.", status=400, mimetype='text/plain')

        try:
            # Headers are passed as a URL-encoded JSON string
            headers_str = request.args.get('headers', '{}')
            headers = json.loads(headers_str)
            # Ensure a Referer is present, as it's often crucial for access
            if 'Referer' not in headers:
                headers['Referer'] = target_url
        except json.JSONDecodeError:
            return Response("Invalid 'headers' JSON in query parameter.", status=400, mimetype='text/plain')

        try:
            response = global_anime_api_service.scraper.get(target_url, headers=headers, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Proxy M3U8: Error fetching from {target_url}: {e}")
            return Response(f"Failed to fetch M3U8 playlist: {e}", status=502, mimetype='text/plain')

        original_m3u8_content = response.text
        base_url = target_url  # Used for resolving relative paths within the playlist

        new_m3u8_lines = []
        for line in original_m3u8_content.splitlines():
            line = line.strip()
            if not line:
                continue

            if line.startswith('#'):
                # Special handling for encryption keys
                if line.startswith('#EXT-X-KEY'):
                    uri_match = re.search(r'URI="([^"]+)"', line)
                    if uri_match:
                        key_uri = uri_match.group(1)
                        absolute_key_uri = urljoin(base_url, key_uri)
                        # The key is also a segment, so it's proxied via /ts
                        proxied_key_uri = f"/api/proxy/ts?url={quote(absolute_key_uri)}&headers={quote(headers_str)}"
                        # Replace the original URI with our proxied one
                        new_line = line.replace(key_uri, proxied_key_uri)
                        new_m3u8_lines.append(new_line)
                    else:
                        new_m3u8_lines.append(line)
                else:
                    new_m3u8_lines.append(line)
            # Check for nested playlists or media segments
            elif line.endswith('.m3u8'):
                absolute_segment_url = urljoin(base_url, line)
                proxied_segment_url = f"/api/proxy/m3u8?url={quote(absolute_segment_url)}&headers={quote(headers_str)}"
                new_m3u8_lines.append(proxied_segment_url)
            else: # Assume any other non-comment line is a media segment
                absolute_segment_url = urljoin(base_url, line)
                proxied_segment_url = f"/api/proxy/ts?url={quote(absolute_segment_url)}&headers={quote(headers_str)}"
                new_m3u8_lines.append(proxied_segment_url)

        new_m3u8_content = "\n".join(new_m3u8_lines)

        resp = Response(new_m3u8_content, mimetype='application/vnd.apple.mpegurl')
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    @staticmethod
    def proxy_ts():
        """
        Fetches a media segment (.ts) or an encryption key and streams it back to the client.
        """
        target_url = request.args.get('url')
        if not target_url:
            return Response("URL parameter is required.", status=400, mimetype='text/plain')

        try:
            headers_str = request.args.get('headers', '{}')
            headers = json.loads(headers_str)
            if 'Referer' not in headers:
                headers['Referer'] = target_url
        except json.JSONDecodeError:
            return Response("Invalid 'headers' JSON in query parameter.", status=400, mimetype='text/plain')

        try:
            response = global_anime_api_service.scraper.get(target_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            def generate():
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            # Pass through original headers but ensure CORS is set
            response_headers = dict(response.headers)
            response_headers['Access-Control-Allow-Origin'] = '*'
            response_headers['Access-Control-Expose-Headers'] = 'Content-Length, Content-Type, Content-Range, Date, Server, Transfer-Encoding'

            return Response(generate(), headers=response_headers, status=response.status_code)

        except requests.exceptions.RequestException as e:
            logger.error(f"Proxy TS: Error fetching from {target_url}: {e}")
            return Response(f"Failed to fetch segment/key: {e}", status=502, mimetype='text/plain')
