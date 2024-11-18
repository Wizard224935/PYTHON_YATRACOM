from flask import Flask
import random
import requests
import json
import time
import os

app = Flask(__name__)

def generate_code():
    """Generate a random code in the exact format Y2GTV?m?m?m?m?m?m?m?m?m?m."""
    base = "Y2GTV"
    suffix = ''.join(
        random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10))
    return base + suffix


def generate_email():
    """Generate a random email address."""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    username = ''.join(
        random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    return f"{username}@{random.choice(domains)}"


def generate_phone():
    """Generate a random 10-digit Indian phone number."""
    return f"9{random.randint(100000000, 999999999)}"


def make_post_request(code, email, phone):
    """Make a POST request to the Yatra API with the generated code."""
    url = "https://secure.yatra.com/PaySwift/gift-voucher/yatra/dom2/1611240003969/check-balance"

    # Custom headers
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json",
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    }

    # Payload
    payload = {
        "superPnr": "1611240003969",
        "emailId": email,
        "amount": 13191,
        "lob": "AIR",
        "isd": "91",
        "mobile": phone,
        "source": "YT",
        "context": "REVIEW",
        "vouchers": [{
            "code": code,
            "type": "PROMO",
            "pin": ""
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None


@app.route('/')
def home():
    """Simple status endpoint."""
    return "Service is running!"


@app.route('/run', methods=['GET'])
def run_task():
    """Endpoint to trigger voucher validation."""
    code = generate_code()
    email = generate_email()
    phone = generate_phone()

    print(f"Generated code: {code}")
    print(f"Generated email: {email}")
    print(f"Generated phone: {phone}")

    response = make_post_request(code, email, phone)

    if response:
        print(f"API Response: {json.dumps(response, indent=2)}")
        return response
    else:
        return {"error": "Request failed or no valid response received."}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no port is specified
    app.run(host="0.0.0.0", port=port)
