# UASpeech EDA & Cleaning Pipeline

Production-style exploratory data analysis and cleaning for the [UASpeech](https://www.isle.illinois.edu/sst/data/uaspeech/) corpus: pair audio with transcriptions, filter by duration and character density (CPS) outliers, and export a cleaned manifest.

## Setup

```bash
cd /home/gera/PycharmProjects/uaspeech-eda-cleaning
pip install -r requirements.txt
```

## Dataset layout (expected)

- **Dataset root** (e.g. `/home/gera/Downloads/uaspeech/UASpeech`):
  - `audio/original/<Speaker>/` — `.wav` files named `<Speaker>_<Block>_<Word>_<Mic>.wav`
  - `mlf/<Speaker>/<Speaker>_word.mlf` — transcriptions (HTK MLF format)

## Usage

Full pipeline (discovery → duration filter → CPS outlier filter → plots → CSV):

```bash
python run_pipeline.py --dataset-root /home/gera/Downloads/uaspeech/UASpeech
```

Options:

- `--output-dir DIR` — where to write `reports/` and `data/` (default: project root)
- `--min-duration SEC` — drop audio shorter than this (default: 3.0)
- `--cps-method {iqr|zscore}` — outlier rule for Characters Per Second (default: iqr)
- `--cps-z-threshold` — when using zscore (default: 3.0)
- `--cps-iqr-mult` — IQR multiplier for bounds (default: 1.5)
- `--sample N` — log a random sample of N records for manual review
- `--n-jobs N` — parallel workers for reading audio
- `-v` — verbose logging

Example with sampling for review:

```bash
python run_pipeline.py --dataset-root /path/to/UASpeech --sample 20
```

## Outputs

- **`reports/`** — distribution plots:
  - `uaspeech_duration_distribution.png`
  - `uaspeech_cps_distribution.png`
- **`data/cleaned_manifest.csv`** — one row per retained recording: `path`, `speaker_id`, `basename`, `transcript`, `duration`, `sample_rate`, `char_count`, `cps`

## Pipeline steps

1. **Discovery** — traverse `audio/original/<Speaker>/*.wav` and pair each file with the word from `mlf/<Speaker>/<Speaker>_word.mlf`.
2. **Duration filter** — keep only recordings with duration ≥ `min_duration_sec` (default 3.0 s).
3. **Metrics** — compute duration and sample rate (via `soundfile`), character count, and **Character Density (CPS)** = `len(transcript) / duration`.
4. **CPS outlier filter** — remove “garbage” (audio/text mismatch) using IQR or Z-score on CPS.
5. **Plots** — histograms for duration and CPS (cleaned set).
6. **Manifest** — save `cleaned_manifest.csv` under `data/`.
7. **Sampling** — optional `sample_for_review(N)` logs N random records for manual checks.

## Programmatic use

```python
from pathlib import Path
from src.uaspeech_processor import UASpeechProcessor

processor = UASpeechProcessor(
    dataset_root=Path("/path/to/UASpeech"),
    min_duration_sec=3.0,
    cps_method="iqr",
    output_dir=Path("."),
)
processor.run()
sample = processor.sample_for_review(10)
```
