import os
import cv2
from ultralytics import YOLO

# Test di tracking basato sul modello addestrato (versione 2)
print("=== TEST RUNTIME DATASET ===")

# Configurazione dei percorsi dinamici
script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(script_dir, "..", ".."))
VIDEO_PATH = os.path.abspath(os.path.join(BASE_DIR, "data", "match", "match.mp4"))

# Punta alla cartella generata dall'addestramento
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "runs", "yolo_match_analysis_convergent-3", "weights", "best.pt"))

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Modello definitivo non trovato in: {MODEL_PATH}\n"
                            f"Aspetta che lo script di addestramento (04) abbia finito!")

# Inizializzazione del modello custom e cattura video
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)

# Spostamento dinamico al fischio d'inizio (minuto 30:45)
MINUTI_DA_SALTARE = 30.75
frame_iniziale = int(MINUTI_DA_SALTARE * 60 * fps)
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_iniziale)

print(f"-> Modello caricato. Pipeline ripristinata a singola inferenza (Veloce).")
print("Apertura finestra video. Premi 'q' per uscire.\n")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Mascheramento come nella versione 1
    altezza, larghezza, _ = frame.shape
    # Taglia la parte superiore dei tifosi che crea rumore
    bordo_superiore = int(altezza * 0.40)
    # Taglia la parte inferiore delle panchine
    bordo_inferiore = int(altezza * 0.95)
    zona_campo = frame[bordo_superiore:bordo_inferiore, 0:larghezza]

    # Esegue il tracking diretto con ByteTrack
    # Ripristina la confidenza a un livello solido perché il modello ora è robusto
    results = model.track(zona_campo, persist=True, tracker="bytetrack.yaml", conf=0.15, iou=0.4, verbose=False)[0]

    if results.boxes is not None and results.boxes.id is not None:
        boxes = results.boxes.xyxy.cpu().numpy()
        track_ids = results.boxes.id.cpu().numpy().astype(int)
        classes = results.boxes.cls.cpu().numpy().astype(int)

        for idx, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            p_id = track_ids[idx]
            classe_rilevata = classes[idx]

            # Gestione delle stampe
            # Gestisce i giocatori in movimento fuori casa
            if classe_rilevata == 0:
                label_text = "AWAY"
                color_box = (255, 255, 255)    # Bianco
            # Gestisce il portiere fuori casa
            elif classe_rilevata == 1:
                label_text = "AWAY_GK"
                color_box = (0, 0, 0)          # Nero
            # Gestisce gli arbitri
            elif classe_rilevata == 2:
                label_text = "REF"
                color_box = (0, 255, 255)      # Giallo
            # Gestisce i giocatori in movimento in casa
            elif classe_rilevata == 3:
                label_text = "HOME"
                color_box = (0, 0, 255)        # Rosso
            # Gestisce il portiere in casa
            elif classe_rilevata == 4:
                label_text = "HOME_GK"
                color_box = (0, 255, 0)        # Verde
            # Gestosce i dubbi in grigio
            else:
                label_text = "UNKNOWN"
                color_box = (128, 128, 128)    # Grigio

            # Rendering grafico
            cv2.rectangle(zona_campo, (x1, y1), (x2, y2), color_box, 2)
            cv2.putText(zona_campo, f"{label_text} #{p_id}", (x1, y1 - 7),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_box, 2)
            cv2.circle(zona_campo, (int((x1 + x2) / 2), y2), 3, color_box, -1)

    # Mostra il feed video a schermo intero
    finestra_ridotta = cv2.resize(zona_campo, (1280, 720))
    cv2.imshow("Active Learning Studio: Modello v2 Serio", finestra_ridotta)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Esecuzione completata.")