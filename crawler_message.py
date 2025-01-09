from telethon import TelegramClient
from telethon import events
from session import Session
from crawler_channel import get_chanell_of_telegram
from filters.crypto_signals_filters import *
import datetime
from model import Currency, ChannelOfTelegram, SignalTable

channels_dict = get_chanell_of_telegram(Session.session_name, Session.api_id, Session.api_hash)
# print(f'your channels:\n{channels_dict}')
channels = [id for id in channels_dict.values()]

for channel in channels_dict.items():
    ch = ChannelOfTelegram.insert(telegram_unique_id=channel[1], user_name=channel[0])
    if ch:
        print(f'channel{ch.telegram_unique_id} added')
    print(channel)

client = TelegramClient(Session.session_name, Session.api_id, Session.api_hash)


@client.on(events.NewMessage(chats=channels))
async def handle_new_message(event):
    sender = await event.get_sender()
    message_text = event.raw_text
    channel_name = event.chat.title if event.chat else "Unknown"
    channel_id = event.chat.id if event.chat else "Unknown"

    print(f"New message in {channel_name} (ID: {channel_id}):\n{message_text}")
    print(f"Sender: {sender.username if sender else 'Unknown'}\n")
    match channel_id:
        case 1374402179:
            # 'CoinCodeCap Futures Signals 🔐'
            if parse_message_coinCodeCap_Futures(message_text):
                val = parse_message_coinCodeCap_Futures(message_text)
                currency = Currency.insert(title=val['currency'])
                signl=SignalTable.insert(cur_title=val.get('currency'),
                                         channel_id=channel_id,
                                         entry_zone=f'start:{val.get("entry_min")} end:{val.get("entry_max")}',
                                         leverage=str(val.get('leverage')),
                                         targets=val.get("take_profit_targets"),
                                         short_or_long=val.get('position'),
                                         stoploss=val.get('stop_loss'),
                                         profit=val.get('profit'),
                                         period_time=str(val.get('period'))

                                         )

        case 1296657365:
            if 'Take profit' in message_text:
                val= parse_message_learn2trade(message_text)
                if val:
                    print(val)
                    currency = Currency.insert(title=val['pair'])
                    signl = SignalTable.insert(cur_title=val.get('pair'),
                                               channel_id=channel_id,
                                               entry_zone=f'start: {val.get("entry")}',
                                               leverage=val.get('leverage'),
                                               targets=str(val.get("take_profits")),
                                               short_or_long=val.get('side'),
                                               stoploss=val.get('stop_loss'),
                                               profit=None,
                                               period_time=None,)
            elif 'Instrument' in message_text:
                val=parse_message_learn2TradeCrypto(message_text)
                if val :
                    currency = Currency.insert(title=val['instrument'])
                    signl = SignalTable.insert(cur_title=val.get('instrument'),
                                               channel_id=channel_id,
                                               entry_zone=f'start: {val.get("entry_price")}',
                                               leverage=None,
                                               targets=str(val.get("target_price")),
                                               short_or_long=val.get('opinion'),
                                               stoploss=val.get('stop_price'),
                                               profit=None,
                                               period_time=None, )


            pass
        case 1429229352:
            # AltSignals.io SPOT VIP
            pass
        case 1440870181:
            # 'AltSignals.io LOW LEV FUTURES VIP'
            pass
        case 1173711569:
            # 'Crypto Signals'
            val = parse_message_crypto_signals(message_text)
            if val:
                if val.get('type') == 'Type 1':
                    print(val)
                    currency = Currency.insert(title=val['pair'])
                    signl = SignalTable.insert(cur_title=val.get('pair'),
                                               channel_id=channel_id,
                                               entry_zone=f'enrtyzone= {val.get("entry_zone")} and breakeven = {val.get("breakeven")}',
                                               leverage=None,
                                               targets=str(val.get("targets")),
                                               short_or_long=val.get('direction'),
                                               stoploss=val.get('stop_loss'),
                                               profit=None,
                                               period_time=None, )
                elif val.get('type') == 'Type 2':
                    currency = Currency.insert(title=val['instrument'])
                    signl = SignalTable.insert(cur_title=val.get('instrument'),
                                               channel_id=channel_id,
                                               entry_zone=f'enrtyzone= {val.get("entry_price")} and risk = {val.get("rrr")}',
                                               leverage=None,
                                               targets=str(val.get("target")),
                                               short_or_long=val.get('opinion'),
                                               stoploss=val.get('stop_loss'),
                                               profit=None,
                                               period_time=None, )
                elif val.get('type') == 'Type 3':
                    currency = Currency.insert(title=val['pair'])
                    signl = SignalTable.insert(cur_title=val.get('pair'),
                                               channel_id=channel_id,
                                               entry_zone=f'enrtyzone= {val.get("entry_price")}',
                                               leverage=val.get('leverage'),
                                               targets=str(val.get("targets")),
                                               short_or_long=val.get('direction'),
                                               stoploss=val.get('stop_loss'),
                                               profit=None,
                                               period_time=None, )


        case 1638463582:
            # 'CoinCodeCap NFT Signals 🔐'
            pass
        case 1200559110:
            # 'CoinCodeCap Spot Signals 🔐'
            pass
        case 1544474547:
            # 'CoinCodeCap High Leverage (High risk) Trades 🔐'
            pass
        case 2379587030:
            val=parse_message_CoinCodeSpot(message_text)
            if val:
                print(val)
                if val.get('Type') == 'Trade Signal':
                    value=val.get('Details')
                    print(value)
                    currency = Currency.insert(title=value.get("Pair"))
                    signl = SignalTable.insert(cur_title=value.get('Pair'),
                                               channel_id=channel_id,
                                               entry_zone=str(value.get('Entry Targets')),
                                               leverage=None,
                                               targets=str(value.get("Take Profit Targets")),
                                               short_or_long=value.get('Type'),
                                               stoploss=value.get('stop_loss'),
                                               profit=None,
                                               period_time=None, )
                elif val.get('Type') == 'Profit Report':
                    value = val.get('Details')
                    currency = Currency.insert(title=value.get("Pair"))
                    signl = SignalTable.insert(cur_title=value.get('Pair'),
                                               channel_id=channel_id,
                                               entry_zone=None,
                                               leverage=None,
                                               targets=None,
                                               short_or_long=None,
                                               stoploss=None,
                                               profit=value.get('Profit'),
                                               period_time=value.get('Period'), )

                elif val.get('Type') == 'Entry Report':
                    value = val.get('Details')
                    currency = Currency.insert(title=value.get("Pair"))
                    signl = SignalTable.insert(cur_title=value.get('Pair'),
                                               channel_id=channel_id,
                                               entry_zone=f'entry confirmed:{value.get("Entry Confirmed")} and average entry price:{value.get("Average Entry Price")}',
                                               leverage=None,
                                               targets=None,
                                               short_or_long=None,
                                               stoploss=None,
                                               profit=None,
                                               period_time=None,)



















with client:
    print("Listening for new messages...")
    client.run_until_disconnected()
