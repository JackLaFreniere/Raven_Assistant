import datetime

def handle_greeting():
    print("[Raven] Hello there!")


def handle_time():
    now = datetime.datetime.now()
    time_str = now.strftime('%I:%M %p').lstrip('0')
    msg = f"[Raven] The time is {time_str}"
    print(msg)
    return msg


def handle_stop():
    print("[Raven] Stop/cancel received.")
