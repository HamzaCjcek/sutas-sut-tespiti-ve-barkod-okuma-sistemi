import os
import base64
from pathlib import Path

from inference_sdk import InferenceHTTPClient


# ==================================================
# ROBOFLOW AYARLARI
# ==================================================

WORKSPACE = "hamza-cicek"

WORKFLOW_ID = "general-segmentation-api"

API_URL = "https://serverless.roboflow.com"


# ==================================================
# DOSYA YOLLARI
# ==================================================

IMAGE_PATH = Path(
    r"C:\Users\ASUS\Downloads\roboflow_dataset\test.jpeg"
)

OUTPUT_PATH = Path(
    r"C:\Users\ASUS\Downloads\roboflow_dataset\sonuc.jpeg"
)


# ==================================================
# MODEL SINIFLARI
# ==================================================

CLASSES = [
    "brand",
    "milk",
    "sutas_milk"
]


# ==================================================
# API KEY
# ==================================================

def get_api_key() -> str:

    api_key = os.getenv("ROBOFLOW_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ROBOFLOW_API_KEY bulunamadı.\n\n"
            "PowerShell'de önce:\n"
            '$env:ROBOFLOW_API_KEY="API_KEYIN"\n\n'
            "sonra:\n"
            "python robo.py"
        )

    return api_key


# ==================================================
# ROBOFLOW CLIENT
# ==================================================

def create_client() -> InferenceHTTPClient:

    return InferenceHTTPClient(
        api_url=API_URL,
        api_key=get_api_key()
    )


# ==================================================
# WORKFLOW ÇALIŞTIR
# ==================================================

def run_workflow(
    client: InferenceHTTPClient,
    image_path: Path
):

    if not image_path.is_file():
        raise FileNotFoundError(
            f"Görsel bulunamadı: {image_path}"
        )

    print("Görsel Roboflow Workflow'a gönderiliyor...")

    response = client.run_workflow(

        workspace_name=WORKSPACE,

        workflow_id=WORKFLOW_ID,

        images={
            "image": str(image_path)
        },

        # ÇOK ÖNEMLİ
        # Workflow şu anda classes bekliyor.
        parameters={
            "classes": CLASSES
        },

        # Workflow değişikliklerinde eski cache'i kullanma.
        use_cache=False
    )

    print("Workflow cevabı alındı.")

    return response

# ==================================================
# RESPONSE NORMALIZE
# ==================================================

def normalize_result(response) -> dict:

    if response is None:
        raise RuntimeError(
            "Roboflow None sonuç döndürdü."
        )

    if isinstance(response, list):

        if len(response) == 0:
            raise RuntimeError(
                "Roboflow boş liste döndürdü."
            )

        result = response[0]

    else:

        result = response

    if not isinstance(result, dict):
        raise RuntimeError(
            f"Beklenmeyen sonuç tipi: {type(result)}"
        )

    return result


# ==================================================
# PREDICTION'LARI AL
# ==================================================

def get_detections(result: dict) -> list:

    predictions_output = result.get("predictions")

    if predictions_output is None:
        return []

    # Senin Workflow çıktın şu formatta:
    #
    # "predictions": {
    #     "image": {...},
    #     "predictions": [...]
    # }

    if isinstance(predictions_output, dict):

        detections = predictions_output.get(
            "predictions",
            []
        )

        if isinstance(detections, list):
            return detections

    # Bazı Workflow'lar direkt liste döndürebilir.
    if isinstance(predictions_output, list):
        return predictions_output

    return []


# ==================================================
# PREDICTION BİLGİLERİNİ YAZDIR
# ==================================================

def print_predictions(result: dict):

    detections = get_detections(result)

    print()
    print("================================")
    print("TAHMİN SONUÇLARI")
    print("================================")

    print(
        f"Toplam detection: {len(detections)}"
    )

    class_counts = {}

    for detection in detections:

        class_name = detection.get(
            "class",
            "bilinmeyen"
        )

        class_counts[class_name] = (
            class_counts.get(class_name, 0) + 1
        )

    print()
    print("Sınıf dağılımı:")

    for class_name, count in class_counts.items():

        print(
            f"{class_name}: {count}"
        )

    print()
    print("İlk 10 detection:")

    for index, detection in enumerate(
        detections[:10],
        start=1
    ):

        class_name = detection.get(
            "class",
            "bilinmeyen"
        )

        confidence = detection.get(
            "confidence",
            0
        )

        x = detection.get("x")
        y = detection.get("y")

        width = detection.get(
            "width"
        )

        height = detection.get(
            "height"
        )

        print(
            f"{index}) "
            f"{class_name} | "
            f"{confidence:.3f} | "
            f"x={x} | "
            f"y={y} | "
            f"w={width} | "
            f"h={height}"
        )


# ==================================================
# ANNOTATED IMAGE AL
# ==================================================

def extract_annotated_image(
    result: dict
) -> str:

    annotated_image = result.get(
        "annotated_image"
    )

    if annotated_image is None:

        raise RuntimeError(
            "Workflow annotated_image döndürmedi.\n"
            f"Gelen alanlar: {list(result.keys())}"
        )

    # ------------------------------------------------
    # String gelirse
    # ------------------------------------------------

    if isinstance(
        annotated_image,
        str
    ):

        encoded_image = annotated_image

    # ------------------------------------------------
    # Dict gelirse
    # ------------------------------------------------

    elif isinstance(
        annotated_image,
        dict
    ):

        encoded_image = (

            annotated_image.get("value")

            or annotated_image.get("base64")

            or annotated_image.get("data")
        )

    else:

        raise RuntimeError(
            "annotated_image formatı tanınmadı: "
            f"{type(annotated_image)}"
        )

    if not encoded_image:

        raise RuntimeError(
            "annotated_image Base64 verisi boş."
        )

    # Eğer:
    #
    # data:image/jpeg;base64,/9j/4AAQ...
    #
    # şeklindeyse başlangıcı kaldır.

    if encoded_image.startswith(
        "data:image"
    ):

        encoded_image = (
            encoded_image.split(
                ",",
                1
            )[1]
        )

    return encoded_image


# ==================================================
# GÖRSELİ KAYDET
# ==================================================

def save_annotated_image(
    result: dict,
    output_path: Path
):

    encoded_image = (
        extract_annotated_image(
            result
        )
    )

    try:

        image_bytes = (
            base64.b64decode(
                encoded_image
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Roboflow'dan gelen görsel "
            "Base64 olarak çözülemedi."
        ) from error

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path.write_bytes(
        image_bytes
    )

    print()
    print(
        "İşaretlenmiş görsel kaydedildi:"
    )

    print(
        output_path
    )


# ==================================================
# MAIN
# ==================================================

def main():

    client = create_client()

    response = run_workflow(
        client=client,
        image_path=IMAGE_PATH
    )

    result = normalize_result(
        response
    )

    print()
    print(
        "Workflow tamamlandı."
    )

    print(
        "Dönen alanlar:",
        list(result.keys())
    )

    print_predictions(
        result
    )

    save_annotated_image(
        result=result,
        output_path=OUTPUT_PATH
    )

    print()
    print(
        "İşlem başarıyla tamamlandı."
    )


# ==================================================
# START
# ==================================================

if __name__ == "__main__":
    main()