# Voice Cloning Script (CSV -> WAV)

This project provides a Python script (`voice_cloning_script.py`) to perform **voice cloning** using [Coqui TTS](https://github.com/coqui-ai/TTS).
It reads text from a **CSV file**, uses a **reference voice sample (.wav)**, and generates speech in `.wav` format.

## Features
- **Simple Variant**: generate one demo sentence.
- **Detailed Variant**: generate one `.wav` per CSV row.
- **Advanced Variant**: generate multilingual speech using the same cloned voice.

## Requirements
- Python 3.10+
- [PyTorch (CPU)](https://pytorch.org/)
- [Coqui TTS](https://github.com/coqui-ai/TTS)

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate

pip3 install --upgrade pip
pip3 install torch --index-url https://download.pytorch.org/whl/cpu
pip3 install TTS
```

## Input Files
- **Voice sample**: `sample_voice.wav` (a few seconds of clean speech)
- **CSV file**: `input.csv`

Example `input.csv`:

```csv
id,text
1,Hello, this is a CSV test.
2,Another sentence to synthesize.
3,This will be spoken in the cloned voice.
```

## Usage

### Simple demo
```bash
python3 voice_cloning_script.py --variant simple --speaker-wav sample_voice.wav --outdir outputs --language en --cpu
```

### Detailed demo (CSV)
```bash
python3 voice_cloning_script.py --variant detailed --speaker-wav sample_voice.wav --input-csv input.csv --outdir outputs --language en --cpu
```

### Advanced multilingual demo
```bash
python3 voice_cloning_script.py --variant advanced --speaker-wav sample_voice.wav --input-csv input.csv --outdir outputs --langs "en,fr-fr,pt-br" --cpu
```

## Output
- `.wav` files are saved under `outputs/` (and `outputs/<lang>/` for advanced).
- Filenames include row index, optional ID, and a short text slug.

## Notes
- Quality depends on the **cleanliness of the reference audio** and the **length/clarity of input text**.
- On CPU, synthesis may take a few seconds per sentence.
- Recommended reference: 10–30 seconds of clear voice.
