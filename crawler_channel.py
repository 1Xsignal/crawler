from telethon.sync import TelegramClient
from session import Session
import asyncio



def get_chanell_of_telegram(session_name, api_id, api_hash):
    with TelegramClient(session_name,api_id, api_hash) as client:
        print("Logged in successfully!")

        dialogs = client.get_dialogs()

        private_channels = [
            (dialog.entity.title, dialog.entity.id)
            for dialog in dialogs
            if dialog.is_channel and dialog.entity.broadcast
        ]

        print("Private Channels:")
        channel_dict={title:channel_id for title, channel_id in private_channels}
        return channel_dict




