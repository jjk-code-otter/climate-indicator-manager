from pathlib import Path
from climind.definitions import ROOT_DIR, METADATA_DIR
from climind.config.config import DATA_DIR
from climind.web.dashboard import Dashboard

if __name__ == "__main__":

    json_file = ROOT_DIR / 'climind' / 'web' / 'dashboard_metadata' / 'key_indicators.json'
    dash = Dashboard.from_json(json_file, METADATA_DIR)

    dash_dir = DATA_DIR / 'ManagedData' / 'Dashboard'
    dash_dir.mkdir(exist_ok=True)
    dash.build(Path(dash_dir))
