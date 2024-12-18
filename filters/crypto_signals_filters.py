import re


def parse_message_crypto_signals(msg):
    data = dict()
    data['currency'] = re.search(r"#(\w+)", msg).group(1)
    data['position'] = "SHORT" if "SHORT" in msg else "LONG"
    data['entry_zone'] = float(re.search(r"Entry Zone: ([\d.]+)", msg).group(1))
    data['accuracy'] = int(re.search(r"Strategy Accuracy: (\d+)%", msg).group(1))
    data['targets'] = [float(x) for x in re.search(r"Targets: ([\d.,\s]+)", msg).group(1).split(',')]
    data['stop_loss'] = float(re.search(r"Stop-Loss: ([\d.]+)", msg).group(1))
    data['breakeven'] = float(re.search(r"after hitting ([\d.]+)", msg).group(1))

    return data


def parse_message_coinCodeCap_Futures(msg):
    data = {}

    if "Cancelled" in msg:
        print('canceled')
        match = re.search(r"#(\w+/\w+)\s+Cancelled", msg)
        if match:
            return match.group(1)
        return None

    elif "Take-Profit" in msg:
        print('take_profit updated')
        data['currency'] = re.search(r"#(\w+/\w+)", msg).group(1)  # استخراج نماد
        data['profit'] = float(re.search(r"Profit:\s([\d.]+)%", msg).group(1))  # استخراج درصد سود
        period_match = re.search(r"Period:\s(\d+)\sHours\s(\d+)\sMinutes", msg)  # استخراج زمان
        hours = int(period_match.group(1))
        minutes = int(period_match.group(2))
        data['period'] = hours * 60 + minutes  # محاسبه مدت زمان به دقیقه
        return data

    elif "LEVERAGE" in msg:
        data['currency'] = re.search(r"(\w+/\w+)", msg).group(1)  # (e.g., GRT/USDT)
        data['position'] = "LONG" if "LONG" in msg else "SHORT"
        data['leverage'] = int(re.search(r"LEVERAGE: (\d+)X", msg).group(1))
        entry_match = re.search(r"Entry Targets: ([\d.]+) - ([\d.]+)", msg)
        data['entry_min'] = float(entry_match.group(2))
        data['entry_max'] = float(entry_match.group(1))
        data['take_profit_targets'] = [float(x) for x in
                                       re.search(r"Take Profit Targets: ([\d. -]+)", msg).group(1).split(" - ")]
        data['stop_loss'] = float(re.search(r"SL: ([\d.]+)", msg).group(1))

        return data

def parse_message_learn2TradeCrypto(msg):
    instrument_match = re.search(r"Instrument:\s*([\w/]+)", msg)  # استخراج Instrument
    opinion_match = re.search(r"My opinion:\s*(.+)", msg)  # استخراج نظر (Buy Stop و ...)
    entry_price_match = re.search(r"Entry price:\s*\$(\d+\.\d+)", msg)  # استخراج Entry price
    stop_match = re.search(r"Stop:\s*\$(\d+\.\d+)", msg)  # استخراج Stop
    target_match = re.search(r"Target:\s*\$(\d+\.\d+)", msg)  # استخراج Target
    risk_match = re.search(r"(My risk setting|Risk Settings):\s*([\d.]+)%", msg)  # استخراج تنظیم ریسک
    rrr_match = re.search(r"RRR:\s*([\d:]+)", msg)  # استخراج RRR

    # بررسی صحت داده‌ها
    if not (
            instrument_match and opinion_match and entry_price_match and stop_match and target_match and risk_match and rrr_match):
        raise ValueError("Invalid message format: Missing required fields.")

    data = {
        "instrument": instrument_match.group(1),
        "opinion": opinion_match.group(1),
        "entry_price": float(entry_price_match.group(1)),
        "stop_price": float(stop_match.group(1)),
        "target_price": float(target_match.group(1)),
        "risk": float(risk_match.group(2)),  # از گروه دوم برای مقدار درصد استفاده می‌کنیم
        "rrr": rrr_match.group(1)
    }

    return data


