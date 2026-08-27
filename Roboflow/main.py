from service.roboflow_client import RoboflowClient
from service.workflow_service import WorkflowService
from service.annotated_image_service import AnnotatedImageService

IMAGE_PATH = r"C:\Users\ASUS\Downloads\roboflow_dataset\test.jpeg"
OUTPUT_FOLDER = r"C:\Users\ASUS\Downloads\roboflow_dataset"


CLASSES = [
    "sutas_milk",
    "milk",
    "brand"
]

roboflow_client = RoboflowClient()

workflow_service = WorkflowService(
    client=roboflow_client.get_client()
)
result = workflow_service.test_image(
    image_path=IMAGE_PATH,
    classes=CLASSES
)
print("Roboflow'dan gelen alanlar:")
print(result.keys())

image_service = AnnotatedImageService()

image_service.save(
    result=result,
    output_folder=OUTPUT_FOLDER
)


print("İşlem tamamlandı.")