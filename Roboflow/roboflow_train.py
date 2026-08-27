import os
import time
from roboflow import Roboflow


WORKSPACE = "hamza-cicek"
PROJECT_ID = "find-milk-rival-and-others"

# Kaç saniye sonra eğitim başlasın?
TRAIN_DELAY_SECONDS = 30


def get_api_key():
    api_key = os.getenv("ROBOFLOW_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ROBOFLOW_API_KEY bulunamadı."
        )

    return api_key


def main():

    # --------------------------------------------------
    # Roboflow bağlantısı
    # --------------------------------------------------

    rf = Roboflow(
        api_key=get_api_key()
    )

    project = (
        rf.workspace(WORKSPACE)
        .project(PROJECT_ID)
    )

    print("Roboflow projesine bağlanıldı.")


    # --------------------------------------------------
    # Yeni Dataset Version oluştur
    # Son etiketlenen veriler de bu version'a girer
    # --------------------------------------------------

    print("Yeni Dataset Version oluşturuluyor...")

    new_version_number = project.generate_version(
        settings={
            "preprocessing": {
                "auto-orient": True,
                "resize": {
                    "width": 640,
                    "height": 640,
                    "format": "Stretch to"
                }
            },

            "augmentation": {}
        }
    )

    print(
        f"Yeni Dataset Version oluşturuldu: "
        f"v{new_version_number}"
    )


    # --------------------------------------------------
    # Version nesnesini al
    # --------------------------------------------------

    version = project.version(
        new_version_number
    )


    # --------------------------------------------------
    # Geri sayım
    # --------------------------------------------------

    print()
    print(
        f"Eğitim {TRAIN_DELAY_SECONDS} saniye "
        f"sonra başlayacak..."
    )

    for remaining in range(
        TRAIN_DELAY_SECONDS,
        0,
        -1
    ):

        print(
            f"\rEğitime kalan süre: "
            f"{remaining} saniye",
            end=""
        )

        time.sleep(1)

    print("\n")


    # --------------------------------------------------
    # YOLO11 NANO TRAINING
    # --------------------------------------------------

    print("YOLO11 Nano eğitimi başlatılıyor...")

    model = version.train(
        model_type="yolov11n",
        checkpoint=None,
        plot_in_notebook=False
    )

    print("Eğitim Roboflow tarafında başlatıldı.")
    print("Dataset Version:", new_version_number)
    print(model)


if __name__ == "__main__":
    main()