"""
Telechargement du dataset Olist depuis Kaggle.

Prerequis : un compte Kaggle et un token API (kaggle.json) place dans ~/.kaggle/.
Si l'API n'est pas configuree, telecharger manuellement le zip depuis
https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce et le dezipper
dans data/raw/.

Usage : python ingestion/download_data.py
"""

import subprocess
import sys
import zipfile
from pathlib import Path

DATASET = "olistbr/brazilian-ecommerce"
RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print("Telechargement de {} vers {} ...".format(DATASET, RAW_DIR))
    try:
        subprocess.run(
            ["kaggle", "datasets", "download", "-d", DATASET, "-p", str(RAW_DIR)],
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "\n[ERREUR] CLI Kaggle indisponible ou non authentifiee.\n"
            "  1. pip install kaggle\n"
            "  2. Kaggle > Account > Create New API Token -> ~/.kaggle/kaggle.json\n"
            "  ou telechargement manuel du zip dans data/raw/."
        )
        return 1

    for archive in RAW_DIR.glob("*.zip"):
        print("Extraction de {} ...".format(archive.name))
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(RAW_DIR)
        archive.unlink()

    csvs = sorted(p.name for p in RAW_DIR.glob("*.csv"))
    print("\n{} fichiers CSV disponibles :".format(len(csvs)))
    for c in csvs:
        print("  - " + c)
    return 0


if __name__ == "__main__":
    sys.exit(main())
