from soran.integrate_stt import run_stt_inference

from Bot_Engine.functions import core_systems


BotControl = core_systems.CoreInterface.integrate()


while True:

    inference_output = run_stt_inference()

    print(inference_output)

    print(BotControl.input_get_response(inference_output))
