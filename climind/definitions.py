from pathlib import Path
import os

ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
METADATA_DIR = ROOT_DIR / "climind" / "metadata_files"