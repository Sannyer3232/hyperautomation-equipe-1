import csv
from pathlib import Path
from playwright.sync_api import sync_playwright

PATH_ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = PATH_ROOT / "resources" / "portal_fake" / "index.html"
CSV_PATH = PATH_ROOT / "resources" / "cadastros_portal_fake_20.csv"
BROWSER_DATA_DIR = PATH_ROOT / "resources" / "browser_data"

def carregar_usuarios(csv_path=CSV_PATH):
    """Carrega os dados dos clientes diretamente do arquivo CSV."""
    usuarios = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            usuarios.append(row)
    return usuarios

