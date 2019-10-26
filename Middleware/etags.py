import json
from hashlib import md5


def generate_etag(data):
    data = json.dumps(data).encode('utf-8')
    etag = md5(data).hexdigest()
    return etag


def check_etag(old_etag, data):
    
    # Generate hash
    new_etag = generate_etag(data)
    
    if new_etag == old_etag:
        return True
    else:
        return False