from fastapi import FastAPI, UploadFile, File, HTTPException
from ultralytics import YOLO

import cv2
import numpy as np
import base64
import torch


# ============================================================
# AYARLAR
# ============================================================

MODEL_PATH = r"C:\Users\ASUS\Desktop\api_python\best.pt"

# SABİT DEĞERLER
PRODUCT_CONF = 0.35
BRAND_CONF = 0.05

IMAGE_SIZE = 1024
IOU = 0.65
MAX_DET = 1500

DEVICE = 0 if torch.cuda.is_available() else "cpu"


# ============================================================
# MODEL
# ============================================================

model = YOLO(MODEL_PATH)

print("Model yüklendi.")
print("Sınıflar:", model.names)
print("Device:", DEVICE)


# ============================================================
# CLASS ID BUL
# ============================================================

def get_class_id(class_name):

    if isinstance(model.names, dict):

        for class_id, name in model.names.items():

            if name == class_name:
                return int(class_id)

    else:

        for class_id, name in enumerate(model.names):

            if name == class_name:
                return class_id

    return None


BRAND_ID = get_class_id("brand")
MILK_ID = get_class_id("milk")
SUTAS_MILK_ID = get_class_id("sutas_milk")


print("brand:", BRAND_ID)
print("milk:", MILK_ID)
print("sutas_milk:", SUTAS_MILK_ID)


if BRAND_ID is None:
    raise RuntimeError(
        "Model içerisinde 'brand' sınıfı bulunamadı."
    )

if MILK_ID is None:
    raise RuntimeError(
        "Model içerisinde 'milk' sınıfı bulunamadı."
    )


PRODUCT_IDS = {MILK_ID}

if SUTAS_MILK_ID is not None:
    PRODUCT_IDS.add(SUTAS_MILK_ID)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Sütaş Görüntü İşleme API"
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def home():

    return {
        "status": "ok",
        "message": "Sütaş modeli hazır"
    }


# ============================================================
# ANALİZ
# ============================================================

@app.post("/api/analyze")
async def analyze(
    image: UploadFile = File(...)
):

    try:

        # ----------------------------------------------------
        # C# TARAFINDAN GELEN RESMİ OKU
        # ----------------------------------------------------

        image_bytes = await image.read()

        np_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            np_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:

            raise HTTPException(
                status_code=400,
                detail="Görsel okunamadı."
            )


        # ----------------------------------------------------
        # YOLO
        #
        # 0.05 kullanmamızın nedeni:
        # brand confidence 0.05'e kadar alınacak.
        #
        # Ürünleri aşağıda ayrıca 0.35 ile filtreliyoruz.
        # ----------------------------------------------------

        results = model.predict(
            source=frame,
            imgsz=IMAGE_SIZE,
            conf=BRAND_CONF,
            iou=IOU,
            max_det=MAX_DET,
            device=DEVICE,
            verbose=False
        )


        result = results[0]


        products = []
        brands = []


        # ----------------------------------------------------
        # BOX'LARI AYIR
        # ----------------------------------------------------

        if result.boxes is not None:

            for box in result.boxes:

                confidence = float(
                    box.conf.item()
                )

                class_id = int(
                    box.cls.item()
                )

                x1, y1, x2, y2 = (
                    box.xyxy[0]
                    .cpu()
                    .numpy()
                    .astype(int)
                    .tolist()
                )


                # --------------------------------------------
                # BRAND
                # sabit minimum = 0.05
                # --------------------------------------------

                if (
                    class_id == BRAND_ID
                    and
                    confidence >= BRAND_CONF
                ):

                    brands.append({

                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,

                        "confidence": confidence

                    })


                # --------------------------------------------
                # ÜRÜN
                # sabit minimum = 0.35
                # --------------------------------------------

                elif (
                    class_id in PRODUCT_IDS
                    and
                    confidence >= PRODUCT_CONF
                ):

                    products.append({

                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,

                        "confidence": confidence,

                        "brandScore": 0.0,

                        "className": "other"

                    })


        # ----------------------------------------------------
        # HER ÜRÜNÜN İÇİNDE SÜTAŞ BRAND VAR MI?
        # ----------------------------------------------------

        for product in products:

            best_brand_score = 0.0


            for brand in brands:

                # brand kutusunun merkezi
                brand_center_x = (
                    brand["x1"]
                    +
                    brand["x2"]
                ) / 2

                brand_center_y = (
                    brand["y1"]
                    +
                    brand["y2"]
                ) / 2


                # Brand merkezi ürün kutusunun içinde mi?
                inside = (

                    product["x1"]
                    <= brand_center_x
                    <= product["x2"]

                    and

                    product["y1"]
                    <= brand_center_y
                    <= product["y2"]

                )


                if inside:

                    best_brand_score = max(
                        best_brand_score,
                        brand["confidence"]
                    )


            product["brandScore"] = (
                best_brand_score
            )


            # -----------------------------------------------
            # SÜTAŞ BRAND EŞİĞİ SABİT = 0.05
            # -----------------------------------------------

            if (
                best_brand_score
                >= BRAND_CONF
            ):

                product["className"] = "sutas"

            else:

                product["className"] = "other"


        # ----------------------------------------------------
        # SAYILAR
        # ----------------------------------------------------

        sutas_count = sum(

            1
            for product in products

            if product["className"] == "sutas"

        )


        other_count = sum(

            1
            for product in products

            if product["className"] == "other"

        )


        total_count = len(products)


        # ----------------------------------------------------
        # RESME BOX ÇİZ
        # ----------------------------------------------------

        output = frame.copy()


        for product in products:

            x1 = product["x1"]
            y1 = product["y1"]

            x2 = product["x2"]
            y2 = product["y2"]


            if product["className"] == "sutas":

                # Sütaş
                color = (255, 0, 255)

                label = (

                    f"Sutas "
                    f"{product['confidence']:.0%} "

                    f"B:"
                    f"{product['brandScore']:.0%}"

                )

            else:

                # Diğer süt
                color = (0, 255, 255)

                label = (

                    f"Diger "
                    f"{product['confidence']:.0%}"

                )


            cv2.rectangle(

                output,

                (x1, y1),

                (x2, y2),

                color,

                2

            )


            cv2.putText(

                output,

                label,

                (
                    x1,
                    max(
                        20,
                        y1 - 5
                    )
                ),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.5,

                color,

                2,

                cv2.LINE_AA

            )


        # ----------------------------------------------------
        # İŞARETLENMİŞ RESMİ BASE64 YAP
        # ----------------------------------------------------

        success, encoded_image = cv2.imencode(
            ".jpg",
            output
        )


        if not success:

            raise HTTPException(
                status_code=500,
                detail="Sonuç resmi oluşturulamadı."
            )


        image_base64 = base64.b64encode(
            encoded_image.tobytes()
        ).decode("utf-8")


        # ----------------------------------------------------
        # C# TARAFINA JSON
        # ----------------------------------------------------

        return {

            "success": True,

            "thresholds": {

                "product": PRODUCT_CONF,

                "sutasBrand": BRAND_CONF

            },

            "counts": {

                "total": total_count,

                "sutas": sutas_count,

                "other": other_count

            },

            "products": [

                {

                    "className":
                        product["className"],

                    "confidence":
                        round(
                            product["confidence"],
                            4
                        ),

                    "brandScore":
                        round(
                            product["brandScore"],
                            4
                        ),

                    "box": {

                        "x1": product["x1"],

                        "y1": product["y1"],

                        "x2": product["x2"],

                        "y2": product["y2"]

                    }

                }

                for product in products

            ],

            # C# tarafında:
            #
            # data:image/jpeg;base64,{annotatedImage}
            #
            # şeklinde img src'ye verilebilir.

            "annotatedImage": image_base64

        }


    except HTTPException:
        raise


    except Exception as error:

        print("HATA:", error)

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


# ============================================================
# ÇALIŞTIR
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000
    )