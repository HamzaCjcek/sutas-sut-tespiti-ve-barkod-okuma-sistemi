from config.roboflow_config import RoboflowConfig
class WorkflowService:

    def __init__(self, client):
        self.client = client

    def test_image(
        self,
        image_path: str,
        classes: list[str]
    ):

        print("Görsel Roboflow'a gönderiliyor...")

        result = self.client.run_workflow(
            workspace_name=RoboflowConfig.WORKSPACE,
            workflow_id=RoboflowConfig.WORKFLOW_ID,

            images={
                "image": image_path
            },

            parameters={
                "classes": classes
            },

            use_cache=False
        )

        if not result:
            raise RuntimeError(
                "Roboflow sonuç döndürmedi."
            )

        if isinstance(result, list):
            result = result[0]

        print("Model testi tamamlandı.")

        return result