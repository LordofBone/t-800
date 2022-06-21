from pathlib import Path

# Root model directory
root_parameters_location = Path(__file__).parent.parent / f"parameters/"

mission_parameters_file = str(root_parameters_location / "mission_parameters.yaml")

# Get parameter refresh time
PARAM_REFRESH = 60
