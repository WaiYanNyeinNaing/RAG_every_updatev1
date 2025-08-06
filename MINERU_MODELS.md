# MinerU Model Architecture & Components

## Overview
MinerU uses multiple specialized deep learning models for different document understanding tasks.

## Core Models

### 1. Layout Analysis Model
**Model Type**: YOLOv8 (You Only Look Once v8)
- **Size**: ~140MB
- **Purpose**: Document layout detection and segmentation
- **Detects**:
  - Text blocks
  - Tables
  - Figures/Images
  - Equations
  - Headers/Footers
  - Lists
- **Accuracy**: 95%+ on standard document layouts

### 2. Table Recognition Model
**Model Type**: TableTransformer (DETR-based)
- **Size**: ~110MB
- **Architecture**: DEtection TRansformer
- **Capabilities**:
  - Table structure detection
  - Row/column boundary identification
  - Cell merging recognition
  - Complex table layouts
- **Output**: Structured table data in JSON/Markdown

### 3. Formula Recognition Model
**Model Type**: LaTeX-OCR (TrOCR variant)
- **Size**: ~200MB
- **Base**: Vision Transformer (ViT) + Transformer decoder
- **Training Data**: 100M+ LaTeX equation pairs
- **Capabilities**:
  - Mathematical symbol recognition
  - Complex equation parsing
  - Matrix/fraction handling
  - Multi-line equation support
- **Output**: LaTeX formatted strings

### 4. OCR Models
**Primary**: PaddleOCR
- **Detection Model**: DBNet++ (~47MB)
- **Recognition Model**: CRNN (~94MB)
- **Languages**: 80+ languages supported
- **Special Features**:
  - Rotated text detection
  - Curved text recognition
  - Multi-language mixing

**Alternative**: EasyOCR
- **Model**: CRAFT + CRNN
- **Languages**: 80+ languages
- **GPU optimized**

## Model Locations

Models are automatically downloaded to:
```
~/.mineru/models/
├── layout/
│   └── yolov8_layout.pt
├── table/
│   └── table_transformer.pth
├── formula/
│   └── latex_ocr_model.pth
└── ocr/
    ├── paddle_det.pdparams
    └── paddle_rec.pdparams
```

## Performance Characteristics

### Speed (on GPU)
- Layout Detection: ~0.5s per page
- Table Extraction: ~1s per table
- Formula Recognition: ~0.3s per equation
- OCR: ~0.2s per text block

### Speed (on CPU)
- Layout Detection: ~2s per page
- Table Extraction: ~3s per table
- Formula Recognition: ~1s per equation
- OCR: ~0.8s per text block

### Accuracy Metrics
- Text Extraction: 98%+ accuracy
- Table Structure: 94% F1 score
- Formula Recognition: 92% exact match
- Layout Detection: 96% mAP

## Configuration

### Select Parsing Method
```python
# In RAGAnything
await rag.process_document_complete(
    file_path="document.pdf",
    parse_method="auto",  # auto, ocr, or txt
    device="cuda:0",      # cuda, cpu, mps (Apple Silicon)
)
```

### Model Source Configuration
```python
# Use different model sources
await rag.process_document_complete(
    file_path="document.pdf",
    source="huggingface",  # huggingface, modelscope, local
)
```

### Language Optimization
```python
# Optimize for specific language
await rag.process_document_complete(
    file_path="document.pdf",
    lang="ch",  # en, ch, ja, ko, etc.
)
```

## Model Selection Logic

MinerU automatically selects models based on:

1. **Document Type**:
   - PDF → Full pipeline
   - Images → OCR + Layout
   - Office → Conversion + Full pipeline

2. **Content Detection**:
   - Tables detected → TableTransformer activated
   - Formulas detected → LaTeX-OCR activated
   - Mixed languages → Multi-language OCR

3. **Performance Mode**:
   - `auto`: Balanced accuracy/speed
   - `ocr`: Maximum accuracy (slower)
   - `txt`: Text extraction only (fastest)

## GPU Acceleration

### Supported GPUs
- NVIDIA CUDA (10.2+)
- Apple Silicon MPS
- AMD ROCm (experimental)

### Memory Requirements
- Minimum: 4GB VRAM
- Recommended: 8GB+ VRAM
- CPU Mode: 8GB+ RAM

## Customization

### Use Custom Models
```python
# Configure custom model paths
os.environ['MINERU_MODEL_DIR'] = '/path/to/custom/models'
```

### Disable Specific Models
```python
await rag.process_document_complete(
    file_path="document.pdf",
    formula=False,  # Disable formula detection
    table=False,    # Disable table detection
)
```

## Comparison with Other Parsers

| Feature | MinerU | Docling | PyPDF | PDFPlumber |
|---------|---------|---------|--------|------------|
| Deep Learning Models | ✅ Yes | ✅ Yes | ❌ No | ❌ No |
| Table Extraction | ✅ Advanced | ✅ Good | ⚠️ Basic | ✅ Good |
| Formula Recognition | ✅ LaTeX | ⚠️ Basic | ❌ No | ❌ No |
| Layout Analysis | ✅ ML-based | ✅ ML-based | ❌ Rule-based | ⚠️ Basic |
| Multi-language | ✅ 80+ | ✅ 50+ | ⚠️ Limited | ⚠️ Limited |
| Speed | ⚡ Fast | ⚡ Fast | ⚡⚡ Very Fast | ⚡ Fast |
| Accuracy | 95%+ | 93%+ | 80%+ | 85%+ |

## Resources

- **MinerU GitHub**: https://github.com/opendatalab/MinerU
- **Model Zoo**: https://huggingface.co/opendatalab
- **Documentation**: https://mineru.readthedocs.io