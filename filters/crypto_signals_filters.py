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


def parse_message_learn2trade(message):
    patterns = {
        "pair_and_side": r"^(\w+)\.([A-Z]+)\s+(SHORT|LONG)",
        "leverage": r"Leverage: (\w+ \d+x)",
        "entry": r"Entry: ([\d\.]+)",
        "take_profits": r"Take profit \d+: ([\d\.]+) \(Success rate: (\d+%)\)",
        "stop_loss": r"Stop loss: ([\d\.]+)",
        "trailing_config": r"Trailing Configuration: Stop: (\w+) - Trigger: Target \((\d+)\)"
    }

    result = {}

    # Extract pair, type, and side (Short/Long)
    pair_and_side_match = re.search(patterns["pair_and_side"], message)
    if pair_and_side_match:
        result["pair"] = pair_and_side_match.group(1)
        result["type"] = pair_and_side_match.group(2)
        result["side"] = pair_and_side_match.group(3)

    # Extract leverage
    leverage_match = re.search(patterns["leverage"], message)
    if leverage_match:
        result["leverage"] = leverage_match.group(1)

    # Extract entry
    entry_match = re.search(patterns["entry"], message)
    if entry_match:
        result["entry"] = float(entry_match.group(1))

    # Extract take profits and success rates
    take_profits = []
    for tp_match in re.finditer(patterns["take_profits"], message):
        take_profits.append({
            "price": float(tp_match.group(1)),
            "success_rate": tp_match.group(2)
        })
    result["take_profits"] = take_profits

    # Extract stop loss
    stop_loss_match = re.search(patterns["stop_loss"], message)
    if stop_loss_match:
        result["stop_loss"] = float(stop_loss_match.group(1))

    # Extract trailing configuration
    trailing_match = re.search(patterns["trailing_config"], message)
    if trailing_match:
        result["trailing_configuration"] = {
            "stop": trailing_match.group(1),
            "trigger_target": int(trailing_match.group(2))
        }

    return result


def parse_message_alt_signal_spot(message):

    if 'Targets:' in message:
        # الگوها برای شناسایی بخش‌های مختلف
        patterns = {
            "currency": r"#(\w+)",
            "entry": r"Entry:\s([\d\.]+\s-\s[\d\.]+)",
            "targets": r"Targets:\s([\d\.\s\-\n]+)",
            "stoploss": r"Stoploss:\s([\d\.]+)"
        }

        # استخراج اطلاعات
        details = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, message)
            if match:
                details[key] = match.group(1).strip()

        # پردازش اهداف برای جداسازی
        if "targets" in details:
            details["targets"] = [float(target) for target in details["targets"].split("-")]

        return details
    else:
        patterns = {
            "currency": r"#(\w+/\w+)",  # استخراج نماد
            "profit": r"Profit:\s([\d\.]+)%",  # استخراج سود
            "loss": r"Loss:\s([\d\.]+)%",  # استخراج ضرر
            "average_entry_price": r"Average Entry Price:\s([\d\.]+)",  # استخراج قیمت ورود
            "period": r"Period:\s(.+)",  # استخراج دوره زمانی
            "status": r"(Take-Profit target \d+|All entry targets achieved|Stop Target Hit)"  # وضعیت پیام
        }

        details = {"exchanges": []}
        # استخراج صرافی‌ها
        exchanges_match = re.search(r"^(.*)\n", message)
        if exchanges_match:
            details["exchanges"] = [ex.strip() for ex in exchanges_match.group(1).split(",")]

        # استخراج داده‌های مختلف
        for key, pattern in patterns.items():
            match = re.search(pattern, message)
            if match:
                details[key] = match.group(1).strip()

        return details




