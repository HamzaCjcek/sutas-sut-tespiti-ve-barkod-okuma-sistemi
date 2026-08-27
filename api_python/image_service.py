import base64

import cv2
import numpy as np


class ImageService:

    # ========================================================
    # BYTE -> OPENCV IMAGE
    # ========================================================

    def decode(
        self,
        image_bytes
    ):

        np_array = np.frombuffer(

            image_bytes,

            dtype=np.uint8

        )

        frame = cv2.imdecode(

            np_array,

            cv2.IMREAD_COLOR

        )

        if frame is None:

            raise ValueError(
                "Görsel okunamadı."
            )

        return frame

    # ========================================================
    # BOX ÇİZ
    # ========================================================

    def draw_products(
        self,
        frame,
        products
    ):

        output = frame.copy()

        for product in products:

            x1 = product["x1"]
            y1 = product["y1"]

            x2 = product["x2"]
            y2 = product["y2"]

            # =================================================
            # SÜTAŞ
            # =================================================

            if (
                product["className"]
                ==
                "sutas"
            ):

                color = (
                    255,
                    0,
                    255
                )

                label = (

                    f"Sutas "
                    f"{product['confidence']:.0%} "

                    f"B:"
                    f"{product['brandScore']:.0%}"

                )

            # =================================================
            # DİĞER
            # =================================================

            else:

                color = (
                    0,
                    255,
                    255
                )

                label = (

                    f"Diger "
                    f"{product['confidence']:.0%}"

                )

            # BOX

            cv2.rectangle(

                output,

                (
                    x1,
                    y1
                ),

                (
                    x2,
                    y2
                ),

                color,

                2

            )

            # LABEL

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

        return output

    # ========================================================
    # OPENCV IMAGE -> BASE64
    # ========================================================

    def to_base64(
        self,
        image
    ):

        success, encoded_image = (
            cv2.imencode(
                ".jpg",
                image
            )
        )

        if not success:

            raise ValueError(
                "Sonuç resmi oluşturulamadı."
            )

        image_base64 = base64.b64encode(

            encoded_image.tobytes()

        ).decode(
            "utf-8"
        )

        return image_base64