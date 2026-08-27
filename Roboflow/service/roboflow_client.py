from inference_sdk import InferenceHTTPClient
from config.roboflow_config import RoboflowConfig


class RoboflowClient:

    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=RoboflowConfig.API_URL,
            api_key=RoboflowConfig.API_KEY
        )

    def get_client(self):
        return self.client