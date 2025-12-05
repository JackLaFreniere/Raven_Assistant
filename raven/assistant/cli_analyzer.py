from raven.assistant.processor import process_command

def start_cli(settings: dict):
    while True:
        command = input("Enter a command >> ")
        process_command(command, settings)