import os
import time
import uuid
import requests

from roboflow import Roboflow


# =========================================================
# CONFIG
# =========================================================

class RoboflowConfig:

    API_KEY = os.getenv("ROBOFLOW_API_KEY")

    WORKSPACE = "hamza-cicek"

    PROJECT_ID = "find-milk-rival-and-others"

    # ŞU ANKİ SON EĞİTTİĞİN MODEL
    MODEL_ID = "hamza-cicek/find-milk-rival-and-others-3-yolo11n-t1"

    API_URL = "https://api.roboflow.com"


# =========================================================
# IMAGE UPLOAD SERVICE
# Sadece resmi Roboflow'a yükler
# =========================================================

class ImageUploadService:

    def __init__(self):

        rf = Roboflow(
            api_key=RoboflowConfig.API_KEY
        )

        self.project = (
            rf.workspace(RoboflowConfig.WORKSPACE)
            .project(RoboflowConfig.PROJECT_ID)
        )

    def upload(self, image_path: str, batch_name: str):

        print("Görsel Roboflow'a yükleniyor...")

        result = self.project.upload(
            image_path=image_path,
            batch_name=batch_name
        )

        print("Görsel yüklendi.")

        return result


# =========================================================
# BATCH SERVICE
# Sadece batch ID bulur
# =========================================================

class BatchService:

    def find_batch_id(self, batch_name: str) -> str:

        url = (
            f"{RoboflowConfig.API_URL}/"
            f"{RoboflowConfig.WORKSPACE}/"
            f"{RoboflowConfig.PROJECT_ID}/batches"
        )

        # Upload sonrası batch'in API'de görünmesi
        # birkaç saniye sürebilir.
        for attempt in range(10):

            response = requests.get(
                url,
                params={
                    "api_key": RoboflowConfig.API_KEY
                },
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            batches = data.get("batches", [])

            for batch in batches:

                if batch.get("name") == batch_name:

                    batch_id = batch.get("id")

                    print(
                        f"Batch bulundu: {batch_id}"
                    )

                    return batch_id

            print(
                f"Batch bekleniyor... "
                f"{attempt + 1}/10"
            )

            time.sleep(2)

        raise RuntimeError(
            f"Batch bulunamadı: {batch_name}"
        )


# =========================================================
# AUTO LABEL SERVICE
# Sadece son model ile Auto Label başlatır
# =========================================================

class AutoLabelService:

    def start(self, batch_id: str):

        url = (
            f"{RoboflowConfig.API_URL}/"
            f"{RoboflowConfig.WORKSPACE}/"
            f"{RoboflowConfig.PROJECT_ID}/autolabel"
        )

        payload = {

            "batchId": batch_id,

            "modelType": "custom_roboflow",

            "modelOptions": {
                "modelId": RoboflowConfig.MODEL_ID
            }
        }

        print()
        print("Auto Label başlatılıyor...")

        print(
            "Model:",
            RoboflowConfig.MODEL_ID
        )

        response = requests.post(
            url,
            params={
                "api_key": RoboflowConfig.API_KEY
            },
            json=payload,
            timeout=60
        )

        if not response.ok:

            raise RuntimeError(
                "\nAuto Label başarısız.\n"
                f"HTTP: {response.status_code}\n"
                f"Cevap: {response.text}"
            )

        result = response.json()

        print("Auto Label başarıyla başlatıldı.")

        print(
            "Job ID:",
            result.get("jobId")
        )

        return result


# =========================================================
# PIPELINE
# Sadece işlemlerin sırasını yönetir
# =========================================================

class RoboflowPipeline:

    def __init__(self):

        if not RoboflowConfig.API_KEY:

            raise RuntimeError(
                "ROBOFLOW_API_KEY bulunamadı."
            )

        self.upload_service = ImageUploadService()

        self.batch_service = BatchService()

        self.auto_label_service = AutoLabelService()

    def run(self, image_path: str):

        # Her yükleme için benzersiz batch
        batch_name = (
            "python-auto-"
            + uuid.uuid4().hex[:10]
        )

        print(
            "Batch:",
            batch_name
        )

        # 1 - Görseli yükle
        self.upload_service.upload(
            image_path=image_path,
            batch_name=batch_name
        )

        # 2 - Batch ID bul
        batch_id = (
            self.batch_service.find_batch_id(
                batch_name=batch_name
            )
        )

        # 3 - Son modelle Auto Label
        result = (
            self.auto_label_service.start(
                batch_id=batch_id
            )
        )

        return result


# =========================================================
# MAIN
# =========================================================

IMAGE_PATH = (
    r"C:\Users\ASUS\Downloads"
    r"\roboflow_dataset\test.jpeg"
)


if __name__ == "__main__":

    RoboflowPipeline().run(IMAGE_PATH)