import re



def parse_message(msg):
    data=dict()
    data['title'] = re.search(r"#(\w+)", msg).group(1)
    data['position'] = "SHORT" if "SHORT" in msg else "LONG"
    data['entry_zone'] = float(re.search(r"Entry Zone: ([\d.]+)", msg).group(1))
    data['accuracy'] = int(re.search(r"Strategy Accuracy: (\d+)%", msg).group(1))
    data['targets'] = [float(x) for x in re.search(r"Targets: ([\d.,\s]+)", msg).group(1).split(',')]
    data['stop_loss'] = float(re.search(r"Stop-Loss: ([\d.]+)", msg).group(1))
    data['breakeven'] = float(re.search(r"after hitting ([\d.]+)", msg).group(1))

    return data