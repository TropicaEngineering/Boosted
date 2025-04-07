import requests
from time import sleep
from datetime import datetime
import json
from telethon import TelegramClient

# Your Telethon API credentials
api_id = 'YOUR_API_ID_HERE'
api_hash = 'YOUR_API_HASH_HERE'
username = '@YOUR_BOT_USERNAME_HERE' # Replace with your pre configured bot's username Trojan / Bonk / Maestro etc e.g. @helenus_trojanbot 

# Toggle for sending messages to Telegram
SEND_TO_TELEGRAM = True  # Set to True to enable sending to Telegram

# DexScreener Boosted Tokens API endpoint
url = "https://api.dexscreener.com/token-boosts/latest/v1"

# Track seen tokens to avoid duplicates
seen_boosts = set()
initial_load_done = False  # Flag to track initial load

# JSON files
tokens_file = 'detected_boosted_tokens.json'  # All detected tokens
sent_tokens_file = 'sent_boosted_tokens.json'  # Tokens sent to Telegram

# Boost filters (configure as needed)
MIN_NEW_BOOST_AMOUNT = 10  # Minimum boost amount just purchased to be considered
MIN_TOTAL_BOOST_AMOUNT = 10  # Minimum cumulative boost amount to consider the token significant

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Load existing tokens from "detected_boosted_tokens.json" to prevent duplicates
def load_existing_tokens():
    global seen_boosts
    try:
        with open(tokens_file, 'r') as file:
            tokens = json.load(file)
            for token in tokens:
                seen_boosts.add(token['tokenAddress'])
        print("Existing boosted tokens loaded.")
        return tokens
    except FileNotFoundError:
        print("No previous tokens found, starting fresh.")
        return []  # Return an empty list if no file found

# Save new tokens to "detected_boosted_tokens.json"
def save_token(token):
    detected_tokens = load_existing_tokens()
    detected_tokens.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tokenAddress": token.get('tokenAddress'),
        "amount": token.get('amount'),
        "totalAmount": token.get('totalAmount')
    })
    with open(tokens_file, 'w') as file:
        json.dump(detected_tokens, file, indent=4)
    print(f"Token saved: {token['tokenAddress']}")

# Save sent tokens to "sent_boosted_tokens.json" with additional info
def save_sent_token(token):
    sent_tokens = load_sent_tokens()
    sent_tokens.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tokenAddress": token.get('tokenAddress'),
        "url": token.get('url'),
        "amount": token.get('amount'),
        "totalAmount": token.get('totalAmount'),
        "description": token.get('description')
    })
    with open(sent_tokens_file, 'w') as file:
        json.dump(sent_tokens, file, indent=4)
    print(f"Token sent to Telegram: {token['tokenAddress']}")

# Load sent tokens from "sent_boosted_tokens.json"
def load_sent_tokens():
    try:
        with open(sent_tokens_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Send contract address to Telegram
async def send_to_telegram(contract_address):
    if SEND_TO_TELEGRAM:
        await client.send_message(username, contract_address)
        print(f"Sent token address to {username}: {contract_address}")

# Fetch and process new boosted tokens
def fetch_latest_boosted_tokens():
    global initial_load_done
    try:
        print(f"Checking for latest boosted tokens at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
        response = requests.get(url)
        if response.status_code == 200:
            tokens = response.json()

            for token in tokens:
                token_address = token.get('tokenAddress')
                amount = token.get('amount', 0)
                total_amount = token.get('totalAmount', 0)

                # Only process Solana tokens with sufficient boosts
                if (token.get('chainId') == 'solana' and 
                    amount >= MIN_NEW_BOOST_AMOUNT and 
                    total_amount >= MIN_TOTAL_BOOST_AMOUNT):
                    
                    # Initial load - just mark tokens as seen
                    if not initial_load_done:
                        seen_boosts.add(token_address)
                        save_token(token)
                    
                    elif token_address not in seen_boosts:
                        # Only process new tokens after initial load
                        seen_boosts.add(token_address)
                        save_token(token)
                        if SEND_TO_TELEGRAM:
                            client.loop.run_until_complete(send_to_telegram(token_address))
                        save_sent_token(token)  # Save to 'sent_boosted_tokens.json' with link and timestamp

                        # Clean and informative console log
                        print(f"New Boosted Token Detected:")
                        print(f"URL: {token.get('url')}")
                        print(f"Token Address: {token_address}")
                        print(f"Boost Amount: {amount}")
                        print(f"Total Boost: {total_amount}")
                        print(f"Description: {token.get('description')}\n{'-' * 20}")

            # Mark the initial load complete
            if not initial_load_done:
                initial_load_done = True
                print("Initial load complete. Future tokens will trigger Telegram messages.")

        else:
            print("Failed to retrieve data:", response.status_code)
    except Exception as e:
        print("Error occurred:", e)

# Initial load of existing tokens and run fetch every 2 seconds
load_existing_tokens()  # Load seen boosts only once
with client:
    while True:
        fetch_latest_boosted_tokens()
        sleep(1)  # Adjust timing as needed