from pathlib import Path
from climind.config.config import DATA_DIR
from climind.definitions import METADATA_DIR
import climind.data_manager.processing as dm

if __name__ == "__main__":
    project_dir = DATA_DIR / "ManagedData"
    data_dir = project_dir / "Data"

    archive = dm.DataArchive.from_directory(METADATA_DIR)

    ts_archive = archive.select({'type': 'gridded'})

    ts_archive.download(data_dir)
