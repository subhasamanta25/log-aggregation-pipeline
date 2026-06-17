import os
import re
import json
import time
import signal
import logging
from datetime import datetime

RUNNING = True

RAW_LOG = "/logs/raw.log"
CLEAN_LOG = "/processed/clean.log"
CONFIG_FILE = "config.json"

LEVEL_PRIORITY = {
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4
}

stats = {
    "total_processed": 0,
    "filtered": 0,
    "duplicates": 0
}

recent_messages = {}

LOG_PATTERN = re.compile( r"\[(.*?)\]\s(\w+)\s\[(.*?)\]\s(.*)" )

def shutdown_handler(signum, frame):
    global RUNNING
    logging.info("Shutdown signal received")
    RUNNING = False

signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {"minimum_level": "WARNING"}

CONFIG = load_config()

def redact_sensitive_data(message):
    ip_pattern = r"\b\d{1,3}(?:\.\d{1,3}){3}\b"
    return re.sub(
        ip_pattern,
        "[REDACTED]",
        message
    )

def is_duplicate(message):
    now = time.time()
    if message in recent_messages:
        if now - recent_messages[message] < 5:
            return True

    recent_messages[message] = now
    return False

def process_line(line):
    match = LOG_PATTERN.match(line.strip())
    if not match:
        return None

    timestamp, level, service, message = match.groups()
    minimum_level = CONFIG["minimum_level"]

    if (
        LEVEL_PRIORITY[level]
        <
        LEVEL_PRIORITY[minimum_level]
    ):
        stats["filtered"] += 1
        return None

    if is_duplicate(message):
        stats["duplicates"] += 1
        return None

    message = redact_sensitive_data(message)

    return (
        f"[{timestamp}] "
        f"{level} "
        f"[{service}] "
        f"{message}"
    )

def write_clean_log(clean_line):
    os.makedirs("/processed", exist_ok=True)

    with open(CLEAN_LOG, "a") as f:
        f.write(clean_line + "\n")

def monitor_logs():

    last_position = 0
    last_stats_time = time.time()

    while RUNNING:

        if not os.path.exists(RAW_LOG):
            logging.warning(
                "Waiting for raw.log..."
            )
            time.sleep(2)
            continue

        try:

            with open(RAW_LOG, "r") as f:

                f.seek(last_position)

                lines = f.readlines()

                last_position = f.tell()

                for line in lines:

                    stats["total_processed"] += 1

                    clean_line = process_line(line)

                    if clean_line:
                        write_clean_log(clean_line)
                        print(clean_line)

        except Exception as e:
            logging.error(e)
            
        if time.time() - last_stats_time >= 10:

            logging.info(
                f"Processed={stats['total_processed']} "
                f"Filtered={stats['filtered']} "
                f"Duplicates={stats['duplicates']}"
            )
            last_stats_time = time.time()
        time.sleep(1)

if __name__ == "__main__":

    logging.info("Log Processor Started..")
    monitor_logs()
    logging.info("Log Processor Stopped..")