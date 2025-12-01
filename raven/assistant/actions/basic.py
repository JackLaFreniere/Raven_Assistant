import datetime

def handle_greeting():
    print("[Raven] Hello there!")


def handle_time():
    now = datetime.datetime.now()
    print(f"[Raven] The time is {now.strftime('%-I:%M %p')}")


def handle_stop():
    print("[Raven] Stop/cancel received.")
