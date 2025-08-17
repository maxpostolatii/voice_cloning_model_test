import argparse
import csv
import re
import sys
from pathlib import Path

from TTS.api import TTS

DEFAULT_MODEL = "tts_models/multilingual/multi-dataset/your_tts"
DEFAULT_OUTPUT_DIR = "outputs"
DEFAULT_LANGUAGE = "en"
DEFAULT_ADVANCED_LANGS = "en,fr-fr,pt-br"

def sanitize_filename(name: str, max_len: int = 100) -> str:
    name = name.strip()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^A-Za-z0-9._-]", "", name)
    return name[:max_len] if name else "utt"

def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)

def load_csv_lines(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    rows = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row. Add a header with a text column.")
        fields_lower = [c.lower() for c in reader.fieldnames]
        candidates = ["text", "sentence", "utterance", "message"]
        text_col_lower = next((c for c in candidates if c in fields_lower), None)
        first_col = reader.fieldnames[0]

        for idx, row in enumerate(reader, start=1):
            if text_col_lower:
                text_key = next(k for k in row.keys() if k.lower() == text_col_lower)
            else:
                text_key = first_col
            text = (row.get(text_key) or "").strip()

            if not text:
                continue

            rid = str(row.get("id") or idx)
            rows.append({"id": rid, "text": text})

    if not rows:
        raise ValueError("No non-empty text lines found in CSV.")
    return rows

def init_tts(model_name: str, use_cpu: bool = True) -> TTS:
    return TTS(model_name=model_name, progress_bar=False, gpu=not use_cpu)

def synth_to_file(tts: TTS, text: str, speaker_wav: Path, out_path: Path, language: str | None = None) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if language:
        tts.tts_to_file(text=text, speaker_wav=str(speaker_wav), language=language, file_path=str(out_path))
    else:
        tts.tts_to_file(text=text, speaker_wav=str(speaker_wav), file_path=str(out_path))

def run_simple(tts: TTS, speaker_wav: Path, out_dir: Path, language: str) -> None:
    sentence = "Hello, this is a quick voice cloning test."
    out_path = out_dir / "simple_demo.wav"
    synth_to_file(tts, sentence, speaker_wav, out_path, language=language)
    print(f"[simple] Wrote: {out_path}")

def run_detailed(tts: TTS, speaker_wav: Path, csv_path: Path, out_dir: Path, language: str) -> None:
    lines = load_csv_lines(csv_path)
    ensure_dir(out_dir)

    for i, row in enumerate(lines, start=1):
        rid = sanitize_filename(row["id"])
        slug = sanitize_filename(" ".join(row["text"].split()[:6]))
        fname = f"{i:03d}_{rid}_{slug}.wav" if slug else f"{i:03d}_{rid}.wav"
        out_path = out_dir / fname
        synth_to_file(tts, row["text"], speaker_wav, out_path, language=language)
        print(f"[detailed] {i}/{len(lines)} -> {out_path}")

def run_advanced(tts: TTS, speaker_wav: Path, csv_path: Path, out_dir: Path, languages: list[str]) -> None:
    lines = load_csv_lines(csv_path)

    for i, row in enumerate(lines, start=1):
        rid = sanitize_filename(row["id"])
        short_slug = sanitize_filename(" ".join(row["text"].split()[:6]))
        for lang in languages:
            subdir = out_dir / lang
            ensure_dir(subdir)
            fname = f"{i:03d}_{rid}_{short_slug or 'utt'}.{lang}.wav"
            out_path = subdir / fname
            synth_to_file(tts, row["text"], speaker_wav, out_path, language=lang)
            print(f"[advanced:{lang}] {i}/{len(lines)} -> {out_path}")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Voice Cloning TTS (CSV -> WAV) with Coqui YourTTS")
    p.add_argument("--variant", choices=["simple", "detailed", "advanced"], default="simple",
                   help="Which demo to run.")
    p.add_argument("--speaker-wav", type=Path, default=Path("sample_voice.wav"),
                   help="Path to your reference voice .wav (static).")
    p.add_argument("--input-csv", type=Path, default=Path("input.csv"),
                   help="Path to CSV file (for detailed/advanced).")
    p.add_argument("--outdir", type=Path, default=Path(DEFAULT_OUTPUT_DIR),
                   help="Output directory for WAV files.")
    p.add_argument("--model", type=str, default=DEFAULT_MODEL,
                   help="Coqui TTS model name.")
    p.add_argument("--language", type=str, default=DEFAULT_LANGUAGE,
                   help="Language code for simple/detailed (e.g., 'en', 'fr-fr').")
    p.add_argument("--langs", type=str, default=DEFAULT_ADVANCED_LANGS,
                   help="Comma-separated language codes for advanced (e.g., 'en,fr-fr,pt-br').")
    p.add_argument("--cpu", action="store_true",
                   help="Force CPU (recommended on macOS).")
    return p.parse_args()

def main():
    args = parse_args()

    if not args.speaker_wav.exists():
        print(f"ERROR: speaker wav not found: {args.speaker_wav}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading model: {args.model} (CPU={'yes' if args.cpu else 'auto'})")
    tts = init_tts(args.model, use_cpu=True if args.cpu else True)

    ensure_dir(args.outdir)

    if args.variant == "simple":
        run_simple(tts, args.speaker_wav, args.outdir, language=args.language)
    elif args.variant == "detailed":
        run_detailed(tts, args.speaker_wav, args.input_csv, args.outdir, language=args.language)
    elif args.variant == "advanced":
        langs = [l.strip() for l in args.langs.split(",") if l.strip()]
        if not langs:
            print("ERROR: no languages provided for advanced variant.", file=sys.stderr)
            sys.exit(1)
        run_advanced(tts, args.speaker_wav, args.input_csv, args.outdir, languages=langs)

    print("Done. See the `outputs` folder for results.")

if __name__ == "__main__":
    main()