import os
from ultralytics import YOLO

# Avvia l'addestramento del modello
print("=== AVVIO ADDESTRAMENTO DATASET SERIO (58 FRAME - 50 EPOCHE) ===")

# Gestione dei file di output
script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(script_dir, "..", ".."))
YAML_PATH = os.path.abspath(os.path.join(BASE_DIR, "data", "dataset_yolo", "data.yaml"))

if not os.path.exists(YAML_PATH):
    raise FileNotFoundError(f"File di configurazione non trovato in: {YAML_PATH}")

# Carica il modello base da cui partire
model = YOLO("yolov8n.pt")

# Fa partire l'addestramento
# ATTENZIONE: stime dei tempi abbastanza lunghi
model.train(
    data=YAML_PATH,
    epochs=50,
    imgsz=640,
    device="cpu",
    project=os.path.join(BASE_DIR, "runs"),
    name="yolo_match_analysis_convergent"   # Nome del modello addestrato
)

print("\n[OK] Addestramento completato con successo!")
# Cartella in cui trovare il modello addestrato
print("I nuovi pesi definitivi sono salvati in: runs/yolo_match_analysis_convergent/weights/best.pt")