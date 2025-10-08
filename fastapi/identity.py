import requests
import json
import config


def validate_mobile_number(msisdn):
    url = "https://payments.relworx.com/api/mobile-money/validate"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/vnd.relworx.v2",
        "Authorization": f"Bearer {config.REMLORX_API_KEY}"
    }
    
    payload = {
        "msisdn": msisdn
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return None

