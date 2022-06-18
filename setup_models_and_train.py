from soran.utils.model_downloader import download_models

from Bot_Engine.utils.sentiment_training_suite import train_all

from Bot_Engine.Chatbot_8.bot_8_trainer import bot_trainer

bot_trainer()
train_all()
download_models()
