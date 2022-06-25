# !/user/bin/env python3

# This is used for calling/configuring all ML systems on the HK

import threading

from ml.camera_obj_detect import ObjectDetector

from config.vision_config import *


def start_machine_vision():
    """
    This is the main function for starting the machine vision system
    :return:
    """
    # Instantiate object detection class
    real_time_analysis = ObjectDetector(vision_active, store_detections, resolution_x, resolution_y,
                                        classes,
                                        object_detect_data_dir, model_path)

    # Thread the analysis stream
    threading.Thread(target=real_time_analysis.run_analysis_stream, daemon=False).start()


if __name__ == "__main__":
    # Perform a test on ML systems
    start_machine_vision()
