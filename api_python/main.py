from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from yolo_service import (
    YoloService
)

from image_service import (
    ImageService
)

from analysis_service import (
    AnalysisService
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Sütaş Görüntü İşleme API"
)


# ============================================================
# SERVİSLER
# ============================================================

yolo_service = (
    YoloService()
)

image_service = (
    ImageService()
)

analysis_service = (
    AnalysisService(
        yolo_service=
            yolo_service,

        image_service=
            image_service
    )
)


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
def home():

    return {

        "status": "ok",

        "message":
            "Sütaş modeli hazır"

    }


# ============================================================
# ANALİZ
# ============================================================

@app.post(
    "/api/analyze"
)
async def analyze(
    image: UploadFile = File(...)
):

    try:

        # C# / Postman tarafından
        # gönderilen resmi oku

        image_bytes = (
            await image.read()
        )

        if not image_bytes:

            raise HTTPException(

                status_code=400,

                detail="Görsel boş."

            )

        # Görüntü işleme servisine gönder

        return (
            analysis_service.analyze(
                image_bytes
            )
        )


    except HTTPException:

        raise


    except ValueError as error:

        raise HTTPException(

            status_code=400,

            detail=str(error)

        )


    except Exception as error:

        print(
            "HATA:",
            error
        )

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