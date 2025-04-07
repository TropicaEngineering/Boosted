
DEXSCREENER - AUTO SNIPE SCRIPTS
======================================================

Summary
-------

What it does:

When a project pays for advertising on DexScreener, the scripts instantly
send a message with the token contract address to a Telegram chat of your choice.
This is useful because most Telegram trading bots can auto-buy tokens just from
receiving a contract address in chat.

So:

  Project pays for DexScreener ad (new token)
        ↓
  Script detects it instantly
        ↓
  Sends contract address to Telegram
        ↓
  Bot auto-buys (if enabled)

No swap script needed — just push from VS Code to chat.

------------------------------------------------------

Scripts
-------

1. Boost Detector

    - Detects ad boosts on DexScreener
    - Sends contract address to a Telegram trading bot (Bonk Bot, Trojan, etc)
    - Bots with auto-buy will purchase the token instantly when CA hits chat
    - Saves you from having to build a swap script
    - Sent tokens are logged in JSON
    - Boost logic: the bigger the boost, the more serious the dev
        e.g. 500 boost = ~$5000 ad spend

    If you catch it early:
      1. You get in before the marketing wave
      2. You know the dev put real money in and likely needs it to work

    - Small boosts (e.g. 10 = $100) don't mean much
    - Use your own judgment — this script surfaces intent

2. Profile Detector

    - Detects when a token pays for a DexScreener profile update (~$300)
    - Earlier signal than boosts, but a bit riskier
    - Can be good for spotting solid upcoming projects
    - Combine with filters like volume/liquidity for better signal
    - Also sends CA to Telegram and logs in JSON

Note: this is beta only. If the market is trash, this won’t help.
Worked well for me in decent conditions — figured I’d share.
DYOR. NFA.

------------------------------------------------------

Prerequisites
-------------

Telegram

    - Set up a mainstream Telegram trading bot (Bonk, Trojan, etc)
    - Bot must support triggering trades via direct contract address
      (e.g. @helenus_trojanbot)
    - If auto-buy is enabled, it’ll trigger a buy when CA is received
    - Or leave auto-buy off and use it for alerts only

Telegram API

    - Go to https://my.telegram.org and create a Telegram dev app
    - Get your api_id and api_hash
    - Script uses Telethon to send messages to Telegram
    - On first run, you'll be prompted to log in
    - Session is saved locally after that

------------------------------------------------------

Technical
---------

Dependencies (install with pip):

    pip install requests telethon

Files Created (auto-handled):

    - detected_boosted_tokens.json           ← all tokens seen with boosts
    - sent_boosted_tokens.json               ← tokens actually sent to Telegram
    - detected_tokens_profile_updates.json   ← all tokens seen with new profiles
    - sent_tokens_new_profile_paid.json      ← tokens sent via profile script

Note: JSONs are reset fresh on each run.

------------------------------------------------------

Cloud Setup (optional)
----------------------

If you're running this on a VPS or cloud instance:

  1. Create a virtualenv or conda environment
  2. Install dependencies:

         pip install requests telethon

  3. Install tmux:

         sudo apt install tmux

  4. Start a tmux session:

         tmux new -s sniper

  5. Run one of the scripts:

         python boosted.py
         # or
         python profile.py

  To detach (leave tmux running):

      Press: Ctrl + B, then D

  To reattach later:

      tmux attach -t sniper

If you want to edit remotely, use VS Code Remote SSH to view logs,
make changes, or update the script live.

------------------------------------------------------

That’s it.

Use it, fork it, edit it, ignore it — up to you.
Just a little tool that helped me during decent market conditions.

Beta only. DYOR. NFA.

======================================================
