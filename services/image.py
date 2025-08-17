from PIL import Image
import os
from io import BytesIO


EXT_META = {
    "jpg": ("JPEG", "image/jpeg"),
    "jpeg": ("JPEG", "image/jpeg"),
    "png": ("PNG", "image/png"),
    "webp": ("WEBP", "image/webp"),
    "bmp": ("BMP", "image/bmp"),
    "tiff": ("TIFF", "image/tiff"),
}


# Convert all imgs from any extension to .jpg
def convert_img(img_bytes: bytes, ext: str, filename: str = "image", quality: int = 90):
    """
    Convert image bytes to another format.

    Args:
        img_bytes (bytes): dữ liệu ảnh gốc
        ext (str): định dạng đích (jpg, png, webp, bmp, tiff)
        filename (str): tên gốc của ảnh (không bắt buộc)
        quality (int): chất lượng cho JPEG/WEBP (1–100)

    Returns:
        (BytesIO, str, str): buffer, content_type, out_filename
    """

    ext = ext.lower().strip()
    if ext not in EXT_META:
        raise ValueError(
            f"Unsupported extension: {ext}. Allowed: {list(EXT_META.keys())}"
        )

    fmt = get_img_format(img_bytes)
    if fmt is None:
        raise ValueError("Invalid or unsupported image file")

    im = Image.open(BytesIO(img_bytes))

    pil_format, content_type = EXT_META[ext]
    if pil_format == "JPEG":
        im = im.convert("RGB")  # tránh lỗi alpha channel

    # Lưu ra buffer
    buf = BytesIO()
    save_kwargs = {"format": pil_format}

    if pil_format in {"JPEG", "WEBP"}:
        q = max(1, min(100, int(quality)))
        save_kwargs.update({"quality": q, "optimize": True})
        if pil_format == "WEBP":
            save_kwargs.update({"method": 6})

    im.save(buf, **save_kwargs)
    buf.seek(0)

    out_name = f"{filename.rsplit('.',1)[0]}.{ 'jpg' if ext=='jpeg' else ext }"
    return buf, content_type, out_name


def get_img_format(img_bytes: bytes):
    try:
        with Image.open(BytesIO(img_bytes)) as im:
            return im.format  # ví dụ "PNG", "JPEG", "WEBP"
    except Exception:
        return None
