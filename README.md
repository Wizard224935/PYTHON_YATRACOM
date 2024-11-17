# Voucher Code Generator

This Python script continuously generates voucher codes and checks their validity using a remote API. If the code is valid, it sends a message to Telegram with the voucher details.

## Features

- Generate random voucher codes, email addresses, and phone numbers.
- Send requests to the Yatra API to validate the voucher codes.
- Notify via Telegram about valid/invalid codes.

## Requirements

This script requires Python 3.x and the `requests` module. You can install it using pip:

```bash
pip install requests
