import base64
import hashlib

def id_from_filename(filename):
    hash_digest = hashlib.sha256(filename.encode()).digest()
    file_id = base64.b64encode(hash_digest).decode()[:8]
    return file_id
