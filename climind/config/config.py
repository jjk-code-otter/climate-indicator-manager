import os
from pathlib import Path

data_dir_env = os.getenv('DATADIR')

DATA_DIR = Path(data_dir_env)
