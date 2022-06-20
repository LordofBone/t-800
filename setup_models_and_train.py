from soran.utils.model_downloader import download_models as download_models_soran

from Bot_Engine.utils.sentiment_training_suite import train_all as train_all_sentiment

from Bot_Engine.Chatbot_8.bot_8_trainer import bot_trainer as bot_trainer_8

from utils.model_downloader import download_and_unzip_model as download_tensorflow_vision_model


def download_all_models_do_all_training():
    """
    This function will download all pre-trained models/data and train the required models
    :return:
    """
    download_models_soran()
    train_all_sentiment()
    bot_trainer_8()
    download_tensorflow_vision_model()


if __name__ == "__main__":
    download_all_models_do_all_training()
