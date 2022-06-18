from Soran.integrate_stt import run_stt_inference

from Bot_Engine.functions import core_systems
from Bot_Engine.utils.sentiment_training_suite import train_all



# train_all()

BotControl = core_systems.CoreInterface.integrate()

inference_output = run_stt_inference()

print(inference_output)

print(BotControl.input_get_response(inference_output))
