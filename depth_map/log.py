from datetime import datetime
import os
import sys

def logger(string, temporary=False, as_file=True,):
    quiet_mode = "-nq" not in sys.argv and "--not-quiet" not in sys.argv and "--loud" not in sys.argv

    # Get the current time and date
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create a logs directory if it does not exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Log name includes the process id
    log_name = f"logs/log-{os.getpid()}.txt"

    if quiet_mode and as_file:
            with open(log_name, "a") as file:
                print(f"{timestamp}: {string}", file=file)
            return
    
    if temporary:
        print(string, end="\r", flush=True)
        return
    
    print(string, flush=True)

def log_separator():
     # determine the character length of terminal line
    terminal_width = os.get_terminal_size().columns

    logger(" ")
    logger("=" * terminal_width)
    logger(" ")
