import os
import cv2
from datetime import datetime
from edge_impulse_linux.image import ImageImpulseRunner
from logger_setup import setup_logger

logger = setup_logger()

def run_inference(model_path: str, image_path: str, save_path: str = None) -> dict:
    result = {}
    model_abs_path = os.path.abspath(model_path)
    image_abs_path = os.path.abspath(image_path)

    with ImageImpulseRunner(model_abs_path) as runner:
        model_info = runner.init()
        logger.info("Model geladen: %s / %s", model_info['project']['owner'], model_info['project']['name'])

        img = cv2.imread(image_abs_path)
        if img is None:
            logger.error("Afbeelding niet leesbaar: %s", image_abs_path)
            raise RuntimeError("Afbeelding niet leesbaar")

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        features, cropped = runner.get_features_from_image_auto_studio_settings(img_rgb)
        res = runner.classify(features)

        logger.debug("Raw inference resultaat: %s", res)

        if "bounding_boxes" in res["result"]:
            boxes = res["result"]["bounding_boxes"]
            result["boxes"] = boxes

            logger.info("Gedetecteerde objecten:")
            best_box = None
            for bb in boxes:
                logger.info("%s (%.2f) - x:%d y:%d w:%d h:%d", bb["label"], bb["value"], bb["x"], bb["y"], bb["width"], bb["height"])
                if not best_box or bb["value"] > best_box["value"]:
                    best_box = bb

            if best_box:
                cropped = cv2.rectangle(cropped,
                                        (best_box["x"], best_box["y"]),
                                        (best_box["x"] + best_box["width"], best_box["y"] + best_box["height"]),
                                        (0, 255, 0), 2)
                result["highest_label"] = best_box["label"]
                result["highest_confidence"] = best_box["value"]
            else:
                result["highest_label"] = "onbekend"
                result["highest_confidence"] = 0.0
        else:
            logger.warning("Geen objectdetectie-resultaten.")
            result["highest_label"] = "onbekend"
            result["highest_confidence"] = 0.0

        if save_path:
            os.makedirs(save_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            label_tag = result["highest_label"]
            filename = f"{timestamp}_{label_tag}.jpg"
            full_path = os.path.join(save_path, filename)
            cv2.imwrite(full_path, cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
            logger.info("Afbeelding opgeslagen: %s", full_path)
            result["saved_image"] = full_path

        return result
