import re


def parse_message_crypto_signals(message):
    try:
        data = {}

        # Detect message type
        if "Crypto Signal Alert" in message:
            # Type 1 message
            data["type"] = "Type 1"
            pair_direction = re.search(r"#(\w+)\s*\|\s*(SHORT|LONG)", message)
            if pair_direction:
                data["pair"] = pair_direction.group(1)
                data["direction"] = pair_direction.group(2)

            entry_zone = re.search(r"Entry Zone:\s*([\d.]+)", message)
            if entry_zone:
                data["entry_zone"] = float(entry_zone.group(1))

            strategy_accuracy = re.search(r"Strategy Accuracy:\s*(\d+)%", message)
            if strategy_accuracy:
                data["strategy_accuracy"] = int(strategy_accuracy.group(1))

            targets = re.search(r"Targets:\s*([\d.,\s]+)", message)
            if targets:
                data["targets"] = [float(target.strip()) for target in targets.group(1).split(",")]

            stop_loss = re.search(r"Stop-Loss:\s*([\d.]+)", message)
            if stop_loss:
                data["stop_loss"] = float(stop_loss.group(1))

            breakeven = re.search(r"Move to breakeven after hitting\s*([\d.]+)", message)
            if breakeven:
                data["breakeven"] = float(breakeven.group(1))

        elif "Instrument" in message:
            # Type 2 message
            data["type"] = "Type 2"
            instrument = re.search(r"Instrument:\s*([\w/]+)", message)
            if instrument:
                data["instrument"] = instrument.group(1)

            opinion = re.search(r"My opinion:\s*(.*)", message)
            if opinion:
                data["opinion"] = opinion.group(1).strip()

            entry_price = re.search(r"Entry price:\s*\$([\d.]+)", message)
            if entry_price:
                data["entry_price"] = float(entry_price.group(1))

            stop = re.search(r"Stop:\s*\$([\d.]+)", message)
            if stop:
                data["stop_loss"] = float(stop.group(1))

            target = re.search(r"Target:\s*\$([\d.]+)", message)
            if target:
                data["target"] = float(target.group(1))

            risk = re.search(r"Risk Settings:(\d+)%", message)
            if risk:
                data["risk"] = int(risk.group(1))

            rrr = re.search(r"RRR:\s*(\d+:\d+)", message)
            if rrr:
                data["rrr"] = rrr.group(1)

        elif "Take profit" in message:

            data["type"] = "Type 3"
            pair_direction = re.search(r"(\w+\.P)\s+(SHORT|LONG)", message)
            if pair_direction:
                data["pair"] = pair_direction.group(1)
                data["direction"] = pair_direction.group(2)

            leverage = re.search(r"Leverage:\s*([\w\s\d]+)", message)
            if leverage:
                data["leverage"] = leverage.group(1).strip()

            entry_price = re.search(r"Entry:\s*([\d.]+)", message)
            if entry_price:
                data["entry_price"] = float(entry_price.group(1))

            targets = re.findall(r"Take profit \d+:\s*([\d.]+) \(Success rate: (\d+)%\)", message)
            if targets:
                data["targets"] = [{"price": float(target[0]), "success_rate": int(target[1])} for target in targets]

            stop_loss = re.search(r"Stop loss:\s*([\d.]+)", message)
            if stop_loss:
                data["stop_loss"] = float(stop_loss.group(1))

            trailing_config = re.search(r"Trailing Configuration: Stop:\s*(\w+)\s*-\s*Trigger:\s*Target\s*\((\d+)\)",
                                        message)
            if trailing_config:
                data["trailing_stop"] = trailing_config.group(1)
                data["trailing_trigger"] = int(trailing_config.group(2))

        else:
            data["error"] = "Unknown message format"

        return data

    except Exception as e:
        return {"error": str(e)}


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
        hours = int(period_match.group(1)) if period_match and period_match.group(1) else 0
        minutes = int(period_match.group(2)) if period_match and period_match.group(2) else 0
        data['period'] = hours * 60 + minutes  # محاسبه مدت زمان به دقیقه
        return data

    elif "LEVERAGE" in msg:
        data['currency'] = re.search(r"(\w+/\w+)", msg).group(1)  # (e.g., GRT/USDT)
        data['position'] = "LONG" if "LONG" in msg else "SHORT"
        data['leverage'] = int(re.search(r"LEVERAGE: (\d+)X", msg).group(1))
        entry_match = re.search(r"Entry Targets: ([\d.]+) - ([\d.]+)", msg)
        data['entry_min'] = float(entry_match.group(2)) if entry_match else 0
        data['entry_max'] = float(entry_match.group(1)) if entry_match else 0
        data['take_profit_targets'] = [x for x in
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
    if 'Target:' in message:
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


        if "targets" in details:
            details["targets"] = [float(target) for target in details["targets"].split("-")]

        return details
    else:
        patterns = {
            "currency": r"#(\w+/\w+)",
            "profit": r"Profit:\s([\d\.]+)%",
            "stoploss": r"Loss:\s([\d\.]+)%",
            "average_entry_price": r"Average Entry Price:\s([\d\.]+)",
            "period": r"Period:\s(.+)",
            "status": r"(Take-Profit target \d+|All entry targets achieved|Stop Target Hit)"
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


def parse_message_AltSignalsioLOW(message):
    if 'Period:' in message:
        patterns_2 = {
            "platforms": r"([\w\s]+Futures(?:, [\w\s]+Futures)*)",  # شناسایی لیست پلتفرم‌ها
            "currency_pair": r"#([\w/]+)",  # شناسایی نوع ارز (مانند LDO/USDT)
            "entry_zone_status": r"(Entered entry zone ✅)",  # وضعیت منطقه ورود
            "period": r"Period:\s*(\d+\s\w+)"  # دوره زمانی
        }

        extracted_data_2 = {}
        for key, pattern in patterns_2.items():
            matches = re.findall(pattern, message)
            extracted_data_2[key] = matches if len(matches) > 1 else matches[0] if matches else None
        return extracted_data_2
    else:
        patterns = {
            "type": r"(LONG|SHORT)",  # شناسایی نوع معامله
            "currency": r"([A-Z]+USDT)",  # شناسایی نوع ارز
            "leverage": r"Leverage: [A-Za-z]+\s([\d.]+X)",  # اهرم
            "entry_zone": r"Entry zone:\s*([\d.]+)-([\d.]+)",  # محدوده ورود
            "targets": r"Target \d+: ([\d.]+)",  # تارگت‌ها
            "stoploss": r"Stoploss: ([\d.]+)"  # حد ضرر
        }

        extracted_data = {}
        for key, pattern in patterns.items():
            matches = re.findall(pattern, message)
            extracted_data[key] = matches if len(matches) > 1 else matches[0] if matches else None

        return extracted_data

def parse_message_CoinCodeCapNFT(message):
    entry_pattern = r"Entry:\s*([\d.]+)-([\d.]+)"
    exit_pattern = r"Exit:\s*([\d.]+)-([\d.]+\+?)"
    risk_pattern = r"Risk:\s*([\d/]+)"
    hold_time_pattern = r"Hold time:\s*(\w+)"
    link_pattern = r"(https?://\S+)"

    # Extract components using regex
    entry = re.search(entry_pattern, message)
    exit_ = re.search(exit_pattern, message)
    risk = re.search(risk_pattern, message)
    hold_time = re.search(hold_time_pattern, message)
    link = re.search(link_pattern, message)

    # Prepare the result dictionary
    result = {
        "entry": (float(entry.group(1)), float(entry.group(2))) if entry else None,
        "exit": (float(exit_.group(1)), float(exit_.group(2).rstrip('+'))) if exit_ else None,
        "risk": risk.group(1) if risk else None,
        "hold_time": hold_time.group(1) if hold_time else None,
        "link": link.group(1) if link else None,
    }

    return result

def parse_message_CoinCodeSpot(message):
    trade_signal_pattern = {
        "Type": r"\b(LONG|SHORT)\b",
        "Pair": r"([A-Z]+/[A-Z]+)",
        "Entry Targets": r"Entry Targets:\s*([\d.]+)\s*-\s*([\d.]+)",
        "Take Profit Targets": r"Take Profit Targets:\s*([\d.]+(?:\s*-\s*[\d.]+)*)"
    }

    profit_report_pattern = {
        "Pair": r"#([A-Z]+/[A-Z]+)",
        "Profit": r"Profit:\s*([\d.]+)% 📈",
        "Period": r"Period:\s*([\w\s\d:]+) ⏰"
    }

    entry_report_pattern = {
        "Platforms": r"^(Binance|Bitget|ByBit|Huobi\.pro|KuCoin|OKX)(?:,?\s*(?:Binance|Bitget|ByBit|Huobi\.pro|KuCoin|OKX))*",
        "Pair": r"#([A-Z]+/[A-Z]+)",
        "Entry Confirmed": r"(Entry\s+\d+\s+✅)",
        "Average Entry Price": r"Average Entry Price:\s*([\d.]+) 💵"
    }

    # Check for trade signal message
    signal_data = {}
    for key, pattern in trade_signal_pattern.items():
        match = re.search(pattern, message)
        signal_data[key] = match.group(1) if match else None

    if signal_data["Type"] and signal_data["Pair"]:
        signal_data["Entry Targets"] = (signal_data.pop("Entry Targets", None), signal_data.pop("Entry Targets", None))
        signal_data["Take Profit Targets"] = signal_data["Take Profit Targets"].split(" - ") if signal_data[
            "Take Profit Targets"] else None
        return {"Type": "Trade Signal", "Details": signal_data}

    # Check for profit report message
    report_data = {}
    for key, pattern in profit_report_pattern.items():
        match = re.search(pattern, message)
        report_data[key] = match.group(1) if match else None

    if report_data["Pair"] and report_data["Profit"] and report_data["Period"]:
        return {"Type": "Profit Report", "Details": report_data}

    # Check for entry report message
    entry_data = {}
    for key, pattern in entry_report_pattern.items():
        match = re.search(pattern, message)
        entry_data[key] = match.group(1) if match else None

    if entry_data["Pair"] and (entry_data["Entry Confirmed"] or entry_data["Average Entry Price"]):
        return {"Type": "Entry Report", "Details": entry_data}

    # If no valid message
    return None


def parse_type_one(message):
    lines = message.split('\n')


    pair = re.search(r'([A-Z]+/[A-Z]+)', lines[0], re.IGNORECASE)
    trade_type = re.search(r'(LONG|SHORT)', lines[0], re.IGNORECASE)
    leverage = re.search(r'LEVERAGE:\s*([\d.]+X)', message, re.IGNORECASE)
    entry_targets = re.search(r'Entry Targets:\s*([\d.]+)', message, re.IGNORECASE)
    take_profit_targets = re.search(r'Take Profit Targets:\s*([\d.\s-]+)', message, re.IGNORECASE)
    take_profit_targets_list = (
        list(map(float, take_profit_targets.group(1).split('-'))) if take_profit_targets else []
    )
    stop_loss = re.search(r'SL:\s*([\d.]+)', message, re.IGNORECASE)


    return {
        'Type': 'Type 1',
        'Pair': pair.group(1) if pair else None,
        'Trade Type': trade_type.group(1) if trade_type else None,
        'Leverage': leverage.group(1) if leverage else None,
        'Entry Target': float(entry_targets.group(1)) if entry_targets else None,
        'Take Profit Targets': take_profit_targets_list,
        'Stop Loss': float(stop_loss.group(1)) if stop_loss else None,
    }

def parse_type_two(message):

    pair = re.search(r'#([A-Z]+/[A-Z]+)', message, re.IGNORECASE)
    avg_entry_price = re.search(r'Average Entry Price:\s*([\d.]+)', message, re.IGNORECASE)
    return {
        'Type': 'Type 2',
        'Pair': pair.group(1) if pair else None,
        'Average Entry Price': float(avg_entry_price.group(1)) if avg_entry_price else None,
    }

def parse_type_three(message):
    pair = re.search(r'#([A-Z]+/[A-Z]+)', message, re.IGNORECASE)
    loss_percentage = re.search(r'Loss:\s*([\d.]+)%', message, re.IGNORECASE)
    return {
        'Type': 'Type 3',
        'Pair': pair.group(1) if pair else None,
        'Stop Loss Triggered': True,
        'Loss Percentage': float(loss_percentage.group(1)) if loss_percentage else None,
    }
def parse_type_four(message):
    pair = re.search(r'#([A-Z]+/[A-Z]+)', message, re.IGNORECASE)
    leverage = re.search(r'Leverage:\s*([\w\s.()X]+)', message, re.IGNORECASE)
    entry_targets = re.findall(r'Entry Targets:\s*\d\)\s*([\d.]+)', message, re.IGNORECASE)
    take_profit_targets = re.findall(r'Take-Profit Targets:\s*\d\)\s*([\d.]+)', message, re.IGNORECASE)
    stop_targets = re.findall(r'Stop Targets:\s*\d\)\s*([\d.]+)', message, re.IGNORECASE)
    return {
        'Type': 'Type 4',
        'Pair': pair.group(1) if pair else None,
        'Leverage': leverage.group(1).strip() if leverage else None,
        'Entry Targets': list(map(float, entry_targets)) if entry_targets else [],
        'Take-Profit Targets': list(map(float, take_profit_targets)) if take_profit_targets else [],
        'Stop Targets': list(map(float, stop_targets)) if stop_targets else [],
    }


def parse_message_CoinCodeHigh(message):
    if re.search(r'Entry Targets:', message, re.IGNORECASE) and \
            re.search(r'Take-Profit Targets:', message, re.IGNORECASE) and \
            re.search(r'Stop Targets:', message, re.IGNORECASE):

        return parse_type_four(message)
    elif re.search(r'(LONG|SHORT)', message, re.IGNORECASE):

        return parse_type_one(message)
    elif re.search(r'All entry targets achieved', message, re.IGNORECASE):

        return parse_type_two(message)
    elif re.search(r'Stoploss', message, re.IGNORECASE):

        return parse_type_three(message)
    else:
        return {"Error": "Unknown message format"}

