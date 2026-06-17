import time
import random
import signal
import logging
from datetime import datetime

RUNNING = True
LOG_FILE = "/logs/raw.log"

SERVICES = [
    "api-service",
    "db-service",
    "cache-service"
]

LEVELS = [
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL"
]

MESSAGES = [
    "User login successful from 192.168.1.100",
    "Connection pool at 85% capacity",
    "Redis connection timeout after 5s",
    "Database query completed",
    "Disk usage exceeded 90%"
]

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

def generate_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = random.choice(LEVELS)
    service = random.choice(SERVICES)
    message = random.choice(MESSAGES)

    return f"[{timestamp}] {level} [{service}] {message}"

def write_log(log_entry):
    try:
        with open(LOG_FILE, "a") as file:
            file.write(log_entry + "\n")
    except Exception as e:
        logging.error(f"Write failed: {e}")

def main():
    logging.info("Log Generator Started..")
    start_time = time.time()
    while RUNNING:
        if time.time() - start_time > 60:
            break

        log_entry = generate_log()
        write_log(log_entry)
        print(log_entry)
        time.sleep(random.uniform(0.5, 1))
    logging.info("Log Generator Stopped..")

if __name__ == "__main__":
    main()