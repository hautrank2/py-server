from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from services.image import convert_img

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}


@app.post("/convert")
async def convert_endpoint(
    file: UploadFile = File(..., description="Ảnh nguồn"),
    ext: str = Form(..., description="Định dạng đầu ra: jpg|jpeg|png|webp|bmp|tiff"),
    quality: int = Form(90, description="Chất lượng cho JPEG/WEBP (1–100)"),
):
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        buf, content_type, out_name = convert_img(
            raw, ext, filename=file.filename, quality=quality
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Convert failed: {e}")

    headers = {"Content-Disposition": f'attachment; filename="{out_name}"'}
    return StreamingResponse(buf, media_type=content_type, headers=headers)
