import os
import time

LOG_DIR = os.path.abspath("../logs")
LOG_FILENAME = "detectie.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILENAME)

def tail_logfile(log_path, lines=20):
    with open(log_path, "r") as f:
        all_lines = f.readlines()
        return all_lines[-lines:]

if __name__ == "__main__":
    print(f"Logviewer gestart – bekijk live: {LOG_PATH}")
    print("Druk op Ctrl+C om te stoppen.\n")

    try:
        last_size = 0
        while True:
            if not os.path.exists(LOG_PATH):
                print("Logbestand nog niet aangemaakt...")
                time.sleep(1)
                continue

            size = os.path.getsize(LOG_PATH)
            if size != last_size:
                last_size = size
                os.system(f"tail -n 20 {LOG_PATH}")
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nLogviewer afgesloten.")
