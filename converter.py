import docling
"""Docling converter setup."""

from docling.datamodel.pipeline_options import (
    EasyOcrOptions,
    PdfPipelineOptions,
    PictureDescriptionVlmOptions,
    TableFormerMode,
)
from docling.document_converter import (
    DocumentConverter,
    ImageFormatOption,
    InputFormat,
    PdfFormatOption,
    WordFormatOption
)

from docling.datamodel.accelerator_options import AcceleratorDevice,AcceleratorOptions
from . import config
import multiprocessing

def build_converter() -> DocumentConverter:
    pipeline_options = PdfPipelineOptions(
        do_ocr=True,
        ocr_options=EasyOcrOptions(lang=["en"]),
        do_table_structure=True,
        do_picture_description=True,
        picture_description_options=PictureDescriptionVlmOptions(repo_id=config.VLM_MODEL_ID),
        generate_picture_images=True,
        accelerator_options=AcceleratorOptions(
            num_threads=multiprocessing.cpu_count(),
            device=AcceleratorDevice.AUTO
        ),
        ocr_batch_size=4,
        layout_batch_size=8,
        table_batch_size=4,
        queue_max_size=100,
        batch_polling_interval_seconds=2.0,
    )
    pipeline_options.table_structure_options.do_cell_matching = True
    pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            InputFormat.DOCX: WordFormatOption(pipeline_options=pipeline_options),
        }
    )
