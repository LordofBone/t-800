import os
import sys

bot_engine_dir = os.path.join(os.path.dirname(__file__), 'Bot_Engine')
chatbot_dir = os.path.join(os.path.dirname(__file__), bot_engine_dir, 'Chatbot_8')
soran_dir = os.path.join(os.path.dirname(__file__), 'soran')

sys.path.append(bot_engine_dir)
sys.path.append(chatbot_dir)
sys.path.append(soran_dir)

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
    bot_trainer_8(fresh_db=True)
    download_tensorflow_vision_model()


if __name__ == "__main__":
    download_all_models_do_all_training()
