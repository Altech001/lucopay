import random
import string
import hashlib
import hmac
import secrets

def generate_order_id(size=8, chars=string.ascii_uppercase + string.digits):

    random_part = ''.join(random.choice(chars) for _ in range(size))
    return f"LXN{random_part}"

def generate_secure_refer_id(size=6, secret_key=None):
    order_id = generate_order_id(size)
    result = {"order_id": order_id}
    
    if secret_key:
        hmac_signature = hmac.new(
            secret_key.encode('utf-8'),
            order_id.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        result["signature"] = hmac_signature
    
    return result

# if __name__ == "__main__":
#     order_id = generate_order_id(size=8)
#     print(f"Generated Order ID: {order_id}")
    
#     # Secure order ID with HMAC
#     secret_key = secrets.token_urlsafe(32)
#     secure_result = generate_secure_order_id(size=8, secret_key=secret_key)
#     print(f"Secure Order ID: {secure_result['order_id']}")
#     if "signature" in secure_result:
#         print(f"HMAC Signature: {secure_result['signature']}")