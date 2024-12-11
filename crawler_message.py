from telethon import TelegramClient
from telethon import events
import asyncio
from session import Session
from crawler_channel import get_chanell_of_telegram



channels_dict=get_chanell_of_telegram(Session.session_name,Session.api_id,Session.api_hash)
print(f'your channels:\n{channels_dict}')
channels = [id for id in  channels_dict.values()]  # جایگزین کنید با یوزرنیم یا ID کانال‌ها



client = TelegramClient(Session.session_name, Session.api_id, Session.api_hash)


@client.on(events.NewMessage(chats=channels))
async def handle_new_message(event):

    sender = await event.get_sender()
    message_text = event.raw_text
    channel_name = event.chat.title if event.chat else "Unknown"

    print(f"New message in {channel_name}:\n{message_text}")
    print(f"Sender: {sender.username if sender else 'Unknown'}\n")



with client:
    print("Listening for new messages...")
    client.run_until_disconnected()