import torch


class Config:
    MODEL_PATH = r"C:\Users\ASUS\Desktop\api_python\best.pt"

    # SABİT EŞİKLER
    PRODUCT_CONF = 0.35
    BRAND_CONF = 0.05

    IMAGE_SIZE = 1024
    IOU = 0.65
    MAX_DET = 1500

    DEVICE = 0 if torch.cuda.is_available() else "cpu"