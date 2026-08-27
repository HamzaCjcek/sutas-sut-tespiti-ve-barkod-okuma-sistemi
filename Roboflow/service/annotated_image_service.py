import base64
from pathlib import Path


class AnnotatedImageService:

    def save(
        self,
        result: dict,
        output_folder: str,
        file_name: str = "sonuc.jpg"
    ):

        if "annotated_image" not in result:
            raise RuntimeError(
                "annotated_image bulunamadı."
            )

        annotated_image = result["annotated_image"]

        print(
            "annotated_image tipi:",
            type(annotated_image)
        )

        if isinstance(annotated_image, dict):
            image_data = (
                annotated_image.get("value")
                or annotated_image.get("base64")
                or annotated_image.get("data")
            )
        else:
            image_data = annotated_image

        if not image_data:
            raise RuntimeError(
                "Görsel verisi bulunamadı."
            )

        if image_data.startswith("data:image"):
            image_data = image_data.split(",", 1)[1]

        image_bytes = base64.b64decode(image_data)

        # Klasör
        folder = Path(output_folder)

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # Dosya yolu
        output_file = folder / file_name

        with open(output_file, "wb") as file:
            file.write(image_bytes)

        print("İşaretlenmiş görsel kaydedildi:")
        print(output_file)

        return str(output_file)