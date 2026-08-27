from ultralytics import YOLO

from config import Config


class YoloService:

    def __init__(self):

        self.model = YOLO(
            Config.MODEL_PATH
        )

        print("Model yüklendi.")
        print("Sınıflar:", self.model.names)
        print("Device:", Config.DEVICE)

        self.brand_id = self._get_class_id(
            "brand"
        )

        self.milk_id = self._get_class_id(
            "milk"
        )

        self.sutas_milk_id = self._get_class_id(
            "sutas_milk"
        )

        print("brand:", self.brand_id)
        print("milk:", self.milk_id)
        print("sutas_milk:", self.sutas_milk_id)

        if self.brand_id is None:
            raise RuntimeError(
                "Model içerisinde 'brand' sınıfı bulunamadı."
            )

        if self.milk_id is None:
            raise RuntimeError(
                "Model içerisinde 'milk' sınıfı bulunamadı."
            )

        self.product_ids = {
            self.milk_id
        }

        if self.sutas_milk_id is not None:

            self.product_ids.add(
                self.sutas_milk_id
            )

    # ========================================================
    # CLASS ID BUL
    # ========================================================

    def _get_class_id(
        self,
        class_name
    ):

        if isinstance(
            self.model.names,
            dict
        ):

            for class_id, name in (
                self.model.names.items()
            ):

                if name == class_name:
                    return int(class_id)

        else:

            for class_id, name in enumerate(
                self.model.names
            ):

                if name == class_name:
                    return class_id

        return None

    # ========================================================
    # YOLO TESPİT
    # ========================================================

    def detect(
        self,
        frame
    ):

        # YOLO 0.05'ten çalışıyor.
        # Bunun sebebi brand tespitlerinin
        # 0.05'e kadar alınabilmesi.
        #
        # Ürünler aşağıda ayrıca
        # 0.35 ile filtreleniyor.

        results = self.model.predict(

            source=frame,

            imgsz=Config.IMAGE_SIZE,

            conf=Config.BRAND_CONF,

            iou=Config.IOU,

            max_det=Config.MAX_DET,

            device=Config.DEVICE,

            verbose=False
        )

        result = results[0]

        products = []
        brands = []

        if result.boxes is None:

            return (
                products,
                brands
            )

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

            # =================================================
            # BRAND
            # minimum = 0.05
            # =================================================

            if (
                class_id == self.brand_id
                and
                confidence >= Config.BRAND_CONF
            ):

                brands.append({

                    "x1": x1,
                    "y1": y1,

                    "x2": x2,
                    "y2": y2,

                    "confidence": confidence

                })

            # =================================================
            # ÜRÜN
            # minimum = 0.35
            # =================================================

            elif (
                class_id in self.product_ids
                and
                confidence >= Config.PRODUCT_CONF
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

        return (
            products,
            brands
        )

    # ========================================================
    # SÜTAŞ / DİĞER AYRIMI
    # ========================================================

    def classify_products(
        self,
        products,
        brands
    ):

        for product in products:

            best_brand_score = 0.0

            for brand in brands:

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

                # Brand merkez noktası
                # ürün kutusunun içinde mi?

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

            # =================================================
            # SÜTAŞ BRAND EŞİĞİ
            # SABİT = 0.05
            # =================================================

            if (
                best_brand_score
                >= Config.BRAND_CONF
            ):

                product["className"] = (
                    "sutas"
                )

            else:

                product["className"] = (
                    "other"
                )

        return products