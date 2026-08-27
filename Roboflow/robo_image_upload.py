import os
from tkinter import Tk, filedialog
from roboflow import Roboflow


# =========================================
# ROBOFLOW AYARLARI
# =========================================

WORKSPACE = "hamza-cicek"
PROJECT = "find-milk-rival-and-others"


# =========================================
# GÖRSEL SEÇ
# =========================================

def select_image():

    root = Tk()
    root.withdraw()

    image_path = filedialog.askopenfilename(
        title="Roboflow'a Yüklenecek Görseli Seç",
        filetypes=[
            ("Görseller", "*.jpg *.jpeg *.png *.webp")
        ]
    )

    root.destroy()

    if not image_path:
        raise RuntimeError("Görsel seçilmedi.")

    return image_path


# =========================================
# ROBOFLOW'A YÜKLE
# =========================================

def upload_image(image_path):

    api_key = os.getenv("ROBOFLOW_API_KEY")

    if not api_key:
        raise RuntimeError(
            "ROBOFLOW_API_KEY bulunamadı."
        )

    rf = Roboflow(
        api_key=api_key
    )

    project = (
        rf.workspace(WORKSPACE)
        .project(PROJECT)
    )

    print("Görsel Roboflow'a yükleniyor...")

    result = project.upload(
        image_path=image_path,
        batch_name="python-upload"
    )

    print("Görsel başarıyla yüklendi.")

    return result


# =========================================
# MAIN
# =========================================

def main():

    image_path = select_image()

    print("Seçilen görsel:")
    print(image_path)

    result = upload_image(
        image_path=image_path
    )

    print("Roboflow cevabı:")
    print(result)


if __name__ == "__main__":
    main()