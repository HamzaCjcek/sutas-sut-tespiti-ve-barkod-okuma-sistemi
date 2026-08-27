from config import Config


class AnalysisService:

    def __init__(
        self,
        yolo_service,
        image_service
    ):

        self.yolo_service = (
            yolo_service
        )

        self.image_service = (
            image_service
        )

    # ========================================================
    # ANA ANALİZ
    # ========================================================

    def analyze(
        self,
        image_bytes
    ):

        # ====================================================
        # 1. RESMİ OKU
        # ====================================================

        frame = (
            self.image_service.decode(
                image_bytes
            )
        )

        # ====================================================
        # 2. YOLO TESPİT
        # ====================================================

        products, brands = (
            self.yolo_service.detect(
                frame
            )
        )

        # ====================================================
        # 3. SÜTAŞ / DİĞER
        # ====================================================

        products = (
            self.yolo_service
            .classify_products(
                products,
                brands
            )
        )

        # ====================================================
        # 4. SAYILAR
        # ====================================================

        sutas_count = sum(

            1

            for product in products

            if (
                product["className"]
                ==
                "sutas"
            )

        )

        other_count = sum(

            1

            for product in products

            if (
                product["className"]
                ==
                "other"
            )

        )

        total_count = len(
            products
        )

        # ====================================================
        # 5. İŞARETLENMİŞ RESİM
        # ====================================================

        output = (
            self.image_service
            .draw_products(
                frame,
                products
            )
        )

        # ====================================================
        # 6. BASE64
        # ====================================================

        image_base64 = (
            self.image_service
            .to_base64(
                output
            )
        )

        # ====================================================
        # 7. JSON RESPONSE
        # ====================================================

        return {

            "success": True,

            "thresholds": {

                "product":
                    Config.PRODUCT_CONF,

                "sutasBrand":
                    Config.BRAND_CONF

            },

            "counts": {

                "total":
                    total_count,

                "sutas":
                    sutas_count,

                "other":
                    other_count

            },

            "products": [

                {

                    "className":
                        product[
                            "className"
                        ],

                    "confidence":
                        round(
                            product[
                                "confidence"
                            ],
                            4
                        ),

                    "brandScore":
                        round(
                            product[
                                "brandScore"
                            ],
                            4
                        ),

                    "box": {

                        "x1":
                            product["x1"],

                        "y1":
                            product["y1"],

                        "x2":
                            product["x2"],

                        "y2":
                            product["y2"]

                    }

                }

                for product in products

            ],

            "annotatedImage":
                image_base64

        }