import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.uaspeech_processor import UASpeechProcessor


def main() -> None:
    parser = argparse.ArgumentParser(description="UASpeech EDA and cleaning pipeline")
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("/home/gera/Downloads/uaspeech/UASpeech"),
        help="Root path of the UASpeech dataset",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROJECT_ROOT,
        help="Directory for reports/ and data/ (default: project root)",
    )
    parser.add_argument(
        "--min-duration",
        type=float,
        default=3.0,
        help="Minimum duration in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--cps-method",
        choices=["iqr", "zscore"],
        default="iqr",
        help="Outlier detection for CPS: iqr or zscore (default: iqr)",
    )
    parser.add_argument(
        "--cps-z-threshold",
        type=float,
        default=3.0,
        help="Z-score threshold when cps-method=zscore (default: 3.0)",
    )
    parser.add_argument(
        "--cps-iqr-mult",
        type=float,
        default=1.5,
        help="IQR multiplier for bounds when cps-method=iqr (default: 1.5)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        metavar="N",
        help="Number of records to sample for manual review (0 = skip)",
    )
    parser.add_argument(
        "--n-jobs",
        type=int,
        default=None,
        help="Parallel jobs for audio reading (default: CPU count - 1)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose (DEBUG) logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    if not args.dataset_root.is_dir():
        logger.error("Dataset root is not a directory: %s", args.dataset_root)
        sys.exit(1)

    processor = UASpeechProcessor(
        dataset_root=args.dataset_root,
        min_duration_sec=args.min_duration,
        cps_method=args.cps_method,
        cps_z_threshold=args.cps_z_threshold,
        cps_iqr_mult=args.cps_iqr_mult,
        output_dir=args.output_dir,
        n_jobs=args.n_jobs,
    )

    processor.run(plot_prefix="uaspeech", manifest_filename="cleaned_manifest.csv")

    if args.sample > 0:
        processor.sample_for_review(n=args.sample)

    logger.info("Pipeline finished. Check %s/reports/ and %s/data/", args.output_dir, args.output_dir)


if __name__ == "__main__":
    main()
