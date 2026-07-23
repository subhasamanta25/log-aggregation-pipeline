import os
import re
import json
import logging
from collections import Counter
from datetime import datetime

CLEAN_LOG = "/processed/clean.log"
REPORT_FILE = "/reports/summary.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

LOG_PATTERN = re.compile( r"\[(.*?)\]\s(\w+)\s\[(.*?)\]\s(.*)" )

def analyze_logs():

    if not os.path.exists(CLEAN_LOG):
        logging.warning("clean.log not found")
        return None

    severity_counter = Counter()

    service_counter = Counter()

    error_counter = Counter()

    timeline_counter = Counter()

    total_logs = 0

    try:

        with open(CLEAN_LOG, "r") as file:

            for line in file:
                match = LOG_PATTERN.match(line.strip())
                if not match:
                    continue

                timestamp, level, service, message = (match.groups())
                total_logs += 1
                severity_counter[level] += 1
                service_counter[service] += 1

                if level in [ "ERROR", "CRITICAL" ]:
                    error_counter[message] += 1

                try:
                    dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    minute_key = dt.strftime( "%Y-%m-%d %H:%M" )
                    timeline_counter[minute_key] += 1

                except Exception:
                    pass

    except Exception as e:

        logging.error(f"Error reading log file: {e}")
        return None

    report = {

        "generated_at":
        datetime.utcnow().isoformat(),

        "total_logs_processed":
        total_logs,

        "severity_breakdown":
        dict(severity_counter),

        "by_service":
        dict(service_counter),

        "top_errors":
        [
            {
                "message": msg,
                "count": count
            }
            for msg, count
            in error_counter.most_common(5)
        ],

        "timeline":
        dict(timeline_counter)
    }
    return report

def save_report(report):
    os.makedirs( "/reports", exist_ok=True )
    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=4)

def print_summary(report):
    print("\n===== LOG REPORT =====")
    print(f"Total Logs: "
        f"{report['total_logs_processed']}"
    )
    print("\nSeverity Breakdown:")

    for level, count in report["severity_breakdown"].items():
        print(f"{level}: {count}")
    print("\nBy Service:")

    for service, count in report[
        "by_service"
    ].items():

        print(f"{service}: {count}")
        
    print("\nTop Errors:")

    for error in report["top_errors"]:
        print(
            f"{error['count']}x - "
            f"{error['message']}"
        )

def main():

    logging.info("Log Analyzer Started..")
    report = analyze_logs()

    if report:
        save_report(report)
        print_summary(report)
        logging.info(
            f"Report saved to "
            f"{REPORT_FILE}"
        )
    logging.info("Log Analyzer Finished..")

if __name__ == "__main__":
    main()
