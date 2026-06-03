import json
import os
import pandas as pd

# 1. Calcolo dinamico dei percorsi
script_dir = os.path.dirname(os.path.abspath(__file__))
file_tracking = os.path.abspath(os.path.join(script_dir, "..", "data", "raw", "tracking", "output0.json"))

print("--- Pipeline Sports Analytics: Calcolo del Centroide ---")

try:
    # 2. Carichiamo il primo blocco di tracking di Opta
    with open(file_tracking, "r", encoding="utf-8") as f:
        frames_grezzi = json.load(f)
    print(f"✅ File output0.json caricato con successo! Fotogrammi trovati: {len(frames_grezzi)}")

    # 3. Estraiamo le coordinate dei giocatori di movimento
    lista_posizioni = []
    for frame in frames_grezzi:
        timestamp = frame["matchtimestamp"]
        for giocatore in frame["players"]:
            if giocatore["role"] != "g":  # Escludiamo il portiere ('g') dal centroide tattico
                lista_posizioni.append({
                    "timestamp": timestamp,
                    "team": giocatore["team"],  # H = Roma, A = Inter
                    "x": giocatore["x"],        # Coordinata X in metri
                    "y": giocatore["y"]         # Coordinata Y in metri
                })

    # Trasformiamo i dati in una tabella Pandas (DataFrame)
    df = pd.DataFrame(lista_posizioni)

    # 4. Calcoliamo la media matematica delle posizioni per ogni istante e per squadra
    centroidi = df.groupby(["timestamp", "team"])[["x", "y"]].mean().reset_index()
    centroidi.columns = ["timestamp", "team", "centroide_x", "centroide_y"]

    print("\n--- Coordinate del Baricentro Squadre (Primi 10 Frame) ---")
    print(centroidi.head(10))

except FileNotFoundError:
    print("❌ Errore: Python non trova il file di tracking.")
    print(f"Verifica che il file output0.json sia esattamente in:\n--> {file_tracking}")