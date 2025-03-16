import os
import time
import cv2
from logger_setup import setup_logger

logger = setup_logger()

DEBUG_FOLDER = os.path.abspath("../debug")

def get_latest_image(folder):
    try:
        files = sorted(
            [f for f in os.listdir(folder) if f.endswith(".jpg")],
            key=lambda x: os.path.getmtime(os.path.join(folder, x)),
            reverse=True
        )
        return os.path.join(folder, files[0]) if files else None
    except Exception as e:
        logger.error("Fout bij ophalen van afbeelding: %s", e)
        return None

if __name__ == "__main__":
    logger.info("Viewer gestart – toont laatste gedetecteerde afbeelding")

    last_displayed = None
    cv2.namedWindow("Laatste detectie", cv2.WINDOW_NORMAL)

    while True:
        latest = get_latest_image(DEBUG_FOLDER)
        if latest and latest != last_displayed:
            img = cv2.imread(latest)
            if img is not None:
                cv2.imshow("Laatste detectie", img)
                logger.info("Afbeelding getoond: %s", latest)
                last_displayed = latest

        if cv2.waitKey(500) & 0xFF == 27:  # ESC sluit af
            logger.info("Viewer afgesloten door gebruiker (ESC).")
            break

        if cv2.getWindowProperty("Laatste detectie", cv2.WND_PROP_VISIBLE) < 1:
            logger.info("Viewer venster gesloten.")
            break

    cv2.destroyAllWindows()
