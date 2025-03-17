import cv2
import os
import time
from logger_setup import setup_logger

logger = setup_logger()

def capture_image(output_path: str, camera_index: int = 0) -> str:
    """
    Maakt een foto via USB-camera en slaat deze op.
    """
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        logger.error("Kan camera niet openen op index %d", camera_index)
        raise RuntimeError(f"Kan camera niet openen op index {camera_index}")

    time.sleep(0.5)
    ret, frame = cap.read()

    if not ret:
        cap.release()
        logger.error("Geen frame ontvangen van camera (index %d)", camera_index)
        raise RuntimeError("Geen frame ontvangen van camera")

    cv2.imwrite(output_path, frame)
    cap.release()

    logger.info("Afbeelding opgeslagen als: %s", output_path)
    return output_path

if __name__ == "__main__":
    output_file = os.path.join(os.path.dirname(__file__), "images/captured_image.jpg")
    capture_image(output_file, camera_index=0)
