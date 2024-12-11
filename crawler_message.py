from telethon import TelegramClient
import asyncio
from session import Session
from crawler_channel import get_chanell_of_telegram

channels = [id for id in get_chanell_of_telegram(Session.session_name,Session.api_id,Session.api_hash).values()]  # جایگزین کنید با یوزرنیم یا ID کانال‌ها


client = TelegramClient(Session.session_name, Session.api_id, Session.api_hash)


async def monitor_channel(channel_username):
    print(f"Listening to channel: {channel_username}")
    async for message in client.iter_messages(channel_username):
        print(f"Channel: {channel_username} | Message ID: {message.id} | Text: {message.text}")


async def main():
    tasks = [monitor_channel(channel) for channel in channels]
    await asyncio.gather(*tasks)


with client:
    client.loop.run_until_complete(main())