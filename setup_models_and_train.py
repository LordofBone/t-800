from soran.utils.model_downloader import download_models as download_models_soran

from Bot_Engine.utils.sentiment_training_suite import train_all as train_all_sentiment

from Bot_Engine.Chatbot_8.bot_8_trainer import bot_trainer as bot_trainer_8

from utils.model_downloader import download_and_unzip_model as download_tensorflow_vision_model

bot_trainer_8()
train_all_sentiment()
download_models_soran()
download_tensorflow_vision_model()
