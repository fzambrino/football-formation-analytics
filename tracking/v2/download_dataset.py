import os
from dotenv import load_dotenv
from roboflow import Roboflow

# Download dei frame già etichettati da Roboflow

# Carica le variabili d'ambiente dal file .env che sta nella radice
load_dotenv()

# Recupera la chiave segreta
api_key = os.getenv("ROBOFLOW_API_KEY")

if not api_key:
    raise ValueError("ERRORE: Chiave API 'ROBOFLOW_API_KEY' non trovata nel file .env!")

# Inizializza Roboflow con la chiave
rf = Roboflow(api_key=api_key)

# Altre credenziali Roboflow
project = rf.workspace("francescos-workspace-mv5ds").project("my-first-project-jv7gm")
version = project.version(4)

# Determina il percorso assoluto della cartella data/dataset_yolo dove conservare i dati
script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(script_dir, "..", ".."))
target_dataset_path = os.path.join(BASE_DIR,"data", "dataset_yolo")

# Scarica il dataset forzando la cartella di destinazione
dataset = version.download("yolov8", location=target_dataset_path)

print(f"\n[OK] Dataset scaricato con successo in: {target_dataset_path}")