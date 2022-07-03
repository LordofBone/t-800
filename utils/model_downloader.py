import wget
import tarfile
from config.vision_config import *
from utils.load_bar_non_iterable import progress_bar


@progress_bar(description="Downloading Tensorflow object detection model", leave=True, increments=10, ascii_bar=False,
              expected_time=20)
def download_model():
    """
    Download the Tensorflow object detection model from the Tensorflow site.
    :return:
    """
    model_url = "http://download.tensorflow.org/models/object_detection/ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz"
    wget.download(model_url, str(object_detect_models_dir))


@progress_bar(description="Unzipping Tensorflow object detection model", leave=True, increments=10,
              ascii_bar=False,
              expected_time=3)
def unzip_model():
    """
    Unzip the Tensorflow object detection model.
    :return:
    """
    tar = tarfile.open(name=model_packed_path, mode="r:gz")
    tar.extractall(path=object_detect_models_dir)
    tar.close()


def download_and_unzip_model():
    download_model()
    unzip_model()


if __name__ == "__main__":
    download_and_unzip_model()
