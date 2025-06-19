# backend/services/anime_api_decryption.py
import requests
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import md5
import json
import logging

logger = logging.getLogger(__name__)

# This key is fetched from the same source as the original Node.js app
DECRYPTION_KEY_URL = "https://raw.githubusercontent.com/itzzzme/megacloud-keys/refs/heads/main/key.txt"

def _get_decryption_key() -> bytes:
    """Fetches the decryption key from the remote source."""
    try:
        response = requests.get(DECRYPTION_KEY_URL, timeout=10)
        response.raise_for_status()
        return response.text.strip().encode('utf-8')
    except requests.RequestException as e:
        logger.error(f"Error fetching decryption key: {e}. Using fallback key.")
        # Fallback key from original JS if fetch fails
        return b"Xy24434w353r4w4r"

def _evpkdf(password: bytes, salt: bytes, key_size: int = 8, iv_size: int = 4) -> tuple[bytes, bytes]:
    """
    Python implementation of OpenSSL's EVP_BytesToKey to derive key and IV.
    This mimics the behavior of CryptoJS.k.EvpKDF.
    """
    derived_key_iv = b''
    d_i = b''
    while len(derived_key_iv) < (key_size + iv_size) * 4: # key_size and iv_size are in 32-bit words
        d_i = md5(d_i + password + salt).digest()
        derived_key_iv += d_i

    # AES key is 256 bits (32 bytes), IV is 128 bits (16 bytes)
    key = derived_key_iv[:32]
    iv = derived_key_iv[32:48]
    return key, iv

def decrypt_source_url(encrypted_data: str, key_bytes: bytes) -> dict | None:
    """
    Decrypts the AES-encrypted source URL from the anime provider.
    """
    try:
        encrypted_data_bytes = base64.b64decode(encrypted_data)

        # The data is structured as Salted__<8-byte salt><ciphertext>
        salt = encrypted_data_bytes[8:16]
        ciphertext = encrypted_data_bytes[16:]

        derived_key, iv = _evpkdf(key_bytes, salt)

        cipher = AES.new(derived_key, AES.MODE_CBC, iv)
        decrypted_padded = cipher.decrypt(ciphertext)

        # Unpad using PKCS7
        decrypted_unpadded = unpad(decrypted_padded, AES.block_size)

        return json.loads(decrypted_unpadded.decode('utf-8'))

    except (ValueError, KeyError) as e:
        logger.error(f"Decryption failed, likely due to incorrect padding or key: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during decryption: {e}", exc_info=True)
        return None
