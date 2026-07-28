import threading
from collections import Counter

import numpy as np
import pandas as pd
import torch
from docling.document_converter import DocumentConverter
from docling_core.types.doc import PictureItem, TableItem, TextItem
from docling_core.types.doc.document import PictureDescriptionData

from . import config

_fallback_captioner = None
_fallback_processor = None
_fallback_device = None
_ocr_reader = None
_model_load_lock = threading.Lock()


def _is_full_page_text(item, doc) -> bool:
    if not item.prov:
        return False
    prov = item.prov[0]
    page = doc.pages.get(prov.page_no)
    if page is None or not page.size:
        return False
    bbox_area = abs(prov.bbox.r - prov.bbox.l) * abs(prov.bbox.t - prov.bbox.b)
    page_area = page.size.width * page.size.height
    if page_area <= 0:
        return False
    return (bbox_area / page_area) >= config.FULL_PAGE_TEXT_AREA_RATIO


def _caption_picture_fallback(picture: PictureItem, doc) -> str:
    global _fallback_captioner, _fallback_processor, _fallback_device
    if _fallback_captioner is None:
        with _model_load_lock:
            if _fallback_captioner is None:
                from transformers import BlipForConditionalGeneration, BlipProcessor

                _fallback_processor = BlipProcessor.from_pretrained(config.BLIP_MODEL_ID)
                _fallback_captioner = BlipForConditionalGeneration.from_pretrained(config.BLIP_MODEL_ID)
                _fallback_device = "cuda" if torch.cuda.is_available() else "cpu"
                _fallback_captioner.to(_fallback_device)
    image = picture.get_image(doc)
    if image is None:
        return ""
    inputs = _fallback_processor(image.convert("RGB"), return_tensors="pt").to(_fallback_device)
    output_ids = _fallback_captioner.generate(**inputs, max_new_tokens=50)
    return _fallback_processor.decode(output_ids[0], skip_special_tokens=True).strip()


def _ocr_picture_text(picture: PictureItem, doc) -> str:
    global _ocr_reader
    image = picture.get_image(doc)
    if image is None:
        return ""
    if _ocr_reader is None:
        with _model_load_lock:
            if _ocr_reader is None:
                import easyocr

                _ocr_reader = easyocr.Reader(["en"], gpu=torch.cuda.is_available())
    results = _ocr_reader.readtext(np.array(image.convert("RGB")), detail=0)
    return " ".join(results).strip()


def extract_structured_data(file_path: str, converter: DocumentConverter) -> list[dict]:    
    result = converter.convert(file_path)   
    doc = result.document

    extracted_items = []
    for item, level in doc.iterate_items():
        if isinstance(item, TextItem):
            extracted_items.append({
                "type": "text",
                "label": item.label,
                "content": item.text,
                "level": level,
                "from_image": _is_full_page_text(item, doc),
            })

        elif isinstance(item, TableItem):
            table_df: pd.DataFrame = item.export_to_dataframe(doc=doc)
            extracted_items.append({
                "type": "table",
                "label": item.label,
                "data": table_df.to_dict(orient="records"),
                "markdown": table_df.to_markdown(index=False),
                "level": level,
            })

        elif isinstance(item, PictureItem):
            caption = next(
                (ann.text for ann in item.annotations if isinstance(ann, PictureDescriptionData)),
                None,
            )
            if not caption:
                caption = _caption_picture_fallback(item, doc)
            ocr_text = _ocr_picture_text(item, doc)
            if ocr_text:
                caption = f"{caption} (text in image: {ocr_text})" if caption else ocr_text
            extracted_items.append({
                "type": "picture",
                "label": item.label,
                "caption": caption,
                "level": level,
            })

    return extracted_items


def summarize_items(file_path: str, converter: DocumentConverter) -> list[dict]:
    items = extract_structured_data(file_path, converter)
    type_counts = Counter(item["type"] for item in items)
    text_label_level_counts = Counter(
        (item["label"], item.get("level")) for item in items if item["type"] == "text"
    )
    print(f"--- {file_path} ---")
    print("type counts:", dict(type_counts))
    print("text (label, level) counts:", dict(text_label_level_counts))
    return items
