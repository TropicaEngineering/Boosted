import requests
from time import sleep
from datetime import datetime
import json
from telethon import TelegramClient

# Your Telethon API credentials
api_id = 'YOUR_API_ID_HERE'
api_hash = 'YOUR API_HASH_HERE'
username = 'YOUR_BOT_USERNAME_HERE'  # Replace with your pre configured bot's username Trojan / Bonk / Maestro etc e.g. @helenus_trojanbot 

# Toggle for sending messages to Telegram
SEND_TO_TELEGRAM = True  # Set to True to enable sending to Telegram

# DexScreener API endpoint
url = "https://api.dexscreener.com/token-profiles/latest/v1"

# Track seen tokens to avoid duplicates
seen_profiles = set()
initial_load_done = False  # Flag to track initial load

# JSON files
tokens_file = 'detected_tokens_profile_updates.json'  # All detected tokens
sent_tokens_file = 'sent_tokens_new_profile_paid.json'  # Tokens sent to Telegram

# Initialize the Telegram client
client = TelegramClient('session_name', api_id, api_hash)

# Load existing tokens from "detected_tokens.json" to prevent duplicates
def load_existing_tokens():
    global seen_profiles
    try:
        with open(tokens_file, 'r') as file:
            tokens = json.load(file)
            for token in tokens:
                seen_profiles.add(token['tokenAddress'])
        print("Existing tokens loaded.")
    except FileNotFoundError:
        print("No previous tokens found, starting fresh.")

# Save new tokens to "detected_tokens.json"
def save_token(token):
    tokens_to_save = list(seen_profiles)  # Convert set to list for JSON
    tokens_to_save.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tokenAddress": token.get('tokenAddress')
    })
    with open(tokens_file, 'w') as file:
        json.dump(tokens_to_save, file, indent=4)
    print(f"Token saved: {token['tokenAddress']}")

# Save sent tokens to "sent_tokens.json" with additional info
def save_sent_token(token):
    sent_tokens = load_sent_tokens()
    sent_tokens.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tokenAddress": token.get('tokenAddress'),
        "url": token.get('url')
    })
    with open(sent_tokens_file, 'w') as file:
        json.dump(sent_tokens, file, indent=4)
    print(f"Token sent to Telegram: {token['tokenAddress']}")

# Load sent tokens from "sent_tokens.json"
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

# Fetch and process new token profiles
def fetch_latest_token_profiles():
    global initial_load_done
    try:
        print(f"Checking for latest token profiles at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}:")
        response = requests.get(url)
        if response.status_code == 200:
            tokens = response.json()

            for token in tokens:
                token_address = token.get('tokenAddress')

                # Only process Solana tokens
                if token.get('chainId') == 'solana':
                    if not initial_load_done:
                        # Mark initial tokens as seen without sending to Telegram
                        seen_profiles.add(token_address)
                        save_token(token)
                    elif token_address not in seen_profiles:
                        # Only process new tokens after initial load
                        seen_profiles.add(token_address)
                        save_token(token)
                        if SEND_TO_TELEGRAM:
                            client.loop.run_until_complete(send_to_telegram(token_address))
                        save_sent_token(token)  # Save to 'sent_tokens.json' with link and timestamp

            # Mark the initial load complete
            if not initial_load_done:
                initial_load_done = True
                print("Initial load complete. Future tokens will trigger Telegram messages.")

        else:
            print("Failed to retrieve data:", response.status_code)
    except Exception as e:
        print("Error occurred:", e)

# Initial load of existing tokens and run fetch every 2 seconds
load_existing_tokens()  # Load seen profiles only once
with client:
    while True:
        fetch_latest_token_profiles()
        sleep(1)  # Adjust timing as needed