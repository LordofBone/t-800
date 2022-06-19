# !/user/bin/env python3

# This is used for calling/configuring all ML systems on the HK

import threading

from camera_obj_detect import ObjectDetector
from utils.yaml_importer import YAMLAccess


def start_machine_vision(show_vision=True, store_detections=False):
    # Instantiate object detection class
    real_time_analysis = ObjectDetector(show_vision, store_detections, YAMLAccess.IM_WIDTH, YAMLAccess.IM_HEIGHT,
                                        YAMLAccess.NUM_CLASSES,
                                        YAMLAccess.OBJ_DETECT_PATH, YAMLAccess.MODEL_NAME)

    # Thread the analysis stream
    threading.Thread(target=real_time_analysis.run_analysis_stream, daemon=False).start()


if __name__ == "__main__":
    # Perform a test on ML systems
    start_machine_vision(True)
