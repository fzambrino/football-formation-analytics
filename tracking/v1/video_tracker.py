import os
import cv2
import numpy as np
from ultralytics import YOLO

# Video tracker basato esclusivamente sui valori HSV (versione 1)

# Recupero dei percorsi
script_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(script_dir, "..", ".."))
# Path della cartella con il video della partita
VIDEO_PATH = os.path.abspath(os.path.join(BASE_DIR, "data", "match", "match.mp4"))

if not os.path.exists(VIDEO_PATH):
    raise FileNotFoundError(f"Video non trovato in: {VIDEO_PATH}")

# Carichamento YOLO Nano
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(VIDEO_PATH)
fps = cap.get(cv2.CAP_PROP_FPS)

# Salto iniziale per andare all'inizio del match (30 minuti e 45 secondi)
# Modificare questo parametro per spostarsi in avanti o indietro
MINUTI_DA_SALTARE = 30.75
frame_iniziale = int(MINUTI_DA_SALTARE * 60 * fps)
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_iniziale)

print(f"-> Salto iniziale eseguito: ci si è spostati al minuto {MINUTI_DA_SALTARE}")
print("Apertura finestra video. Premi 'q' per uscire.\n")

frame_counter = frame_iniziale

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_counter += 1

    altezza, larghezza, _ = frame.shape
    # Definisce il taglio superiore al 40% (0.40) per eliminare del tutto i tifosi sullo sfondo
    bordo_superiore = int(altezza * 0.40)
    # Definisce il taglio inferiore al 5% (1-0.95) per eliminare le panchine in primo piano
    bordo_inferiore = int(altezza * 0.95)
    zona_campo = frame[bordo_superiore:bordo_inferiore, 0:larghezza]

    # Tracking YOLO
    results = model.track(zona_campo, classes=[0], persist=True, tracker="bytetrack.yaml", verbose=False)[0]

    if results.boxes is not None and results.boxes.id is not None:
        boxes = results.boxes.xyxy.cpu().numpy()
        track_ids = results.boxes.id.cpu().numpy().astype(int)

        for idx, box in enumerate(boxes):
            x1, y1, x2, y2 = map(int, box)
            p_id = track_ids[idx]

            h_box = y2 - y1
            w_box = x2 - x1

            if h_box > w_box and h_box > 20:
                # Stringe l'inquadratura per raccogliere solo la maglia, lasciando fuori l'erba laterale
                busto = zona_campo[y1 + int(h_box * 0.15):y1 + int(h_box * 0.35), x1 + int(w_box * 0.3):x2 - int(w_box * 0.3)]
                if busto.size == 0:
                    continue

                # Estrazione e conversione dei valori medi in HSV
                busto_hsv = cv2.cvtColor(busto, cv2.COLOR_BGR2HSV)
                colore_medio_hsv = busto_hsv.mean(axis=(0, 1))

                hue = int(colore_medio_hsv[0])
                saturation = int(colore_medio_hsv[1])
                value = int(colore_medio_hsv[2])


                # Gestione per i giocatori in maglia bianca A
                if saturation < 50 and value > 160:
                    color_box = (255, 255, 255)  # Bianco
                    team_name = "A"

                # Gestione per gli arbitri in giallo
                elif value < 75:
                    color_box = (0, 255, 255)    # Giallo
                    team_name = "STAFF/REF"

                # Gestione per i giocatori in maglia rossa H
                elif (hue < 35 or hue > 155) and saturation > 40:
                    color_box = (0, 0, 255)      # Rosso
                    team_name = "H"

                # Gestione dei tracciamenti dubbi
                else:
                    color_box = (128, 128, 128)  # Grigio
                    team_name = f"DOUBT H:{hue} S:{saturation}"

                # Disegno dei rettangoli e dei testi
                cv2.rectangle(zona_campo, (x1, y1), (x2, y2), color_box, 2)
                cv2.putText(zona_campo, f"{team_name} #{p_id}", (x1, y1 - 7),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, color_box, 2)
                cv2.circle(zona_campo, (int((x1 + x2) / 2), y2), 3, color_box, -1)

    # Rendering video
    finestra_ridotta = cv2.resize(zona_campo, (1280, 720))
    cv2.imshow("Laboratorio CV: Tracking Avanzato HSV", finestra_ridotta)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Laboratorio terminato.")