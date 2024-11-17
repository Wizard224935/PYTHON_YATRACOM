import requests

def get_public_ip():
    try:
        # Using ipify API to get the public IP address
        response = requests.get("https://api.ipify.org?format=json")
        data = response.json()
        return data['ip']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching IP address: {e}")
        return None

if __name__ == "__main__":
    ip = get_public_ip()
    if ip:
        print(f"Your public IP address is: {ip}")
    else:
        print("Could not retrieve public IP address.")