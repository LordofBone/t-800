from pathlib import Path

# Root model directory
root_models_dir = Path(__file__).parent.parent / f"models/"

# Path to the objection detection model directory
object_detect_models_dir = Path(__file__).parent.parent / f"models/tensorflow"

# Resolution configuration for the PiCamera
resolution_x = 1024
resolution_y = 768

# Framerate for the PiCamera
framerate = 10

# Class/model configuration for Tensorflow in object detection
# Maximum classes that can be detected per-frame
classes = 90
# Name of the detection model
model_packed_name = "ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz"
model_packed_path = str(object_detect_models_dir / model_packed_name)
model_name = "ssdlite_mobilenet_v2_coco_2018_05_09"
model_path = str(object_detect_models_dir / model_name)