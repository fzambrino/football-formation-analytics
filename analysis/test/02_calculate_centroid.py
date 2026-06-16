import json
import os
import pandas as pd

# TEST: PRIMO TENTATIVO DI CALCOLO DEL CENTROIDE DI SQUADRA

# Calcolo dinamico dei percorsi
script_dir = os.path.dirname(os.path.abspath(__file__))
file_tracking = os.path.abspath(os.path.join(script_dir, "..", "..", "data", "raw", "tracking", "output0.json"))

print("--- Pipeline Sports Analytics: Calcolo del Centroide ---")

try:
    # Carica il primo blocco di tracking
    with open(file_tracking, "r", encoding="utf-8") as f:
        frames_grezzi = json.load(f)
    print(f"File output0.json caricato con successo. Fotogrammi trovati: {len(frames_grezzi)}")

    # Estrazione delle coordinate dei giocatori di movimento
    lista_posizioni = []
    for frame in frames_grezzi:
        timestamp = frame["matchtimestamp"]
        for giocatore in frame["players"]:
            if giocatore["role"] != "g":  # Esclusione del portiere ('g') dal centroide tattico
                lista_posizioni.append({
                    "timestamp": timestamp,
                    "team": giocatore["team"],  # H (in casa), A (fuori casa)
                    "x": giocatore["x"],        # Coordinata X in metri
                    "y": giocatore["y"]         # Coordinata Y in metri
                })

    # Trasformazione dei dati in una tabella Pandas (DataFrame)
    df = pd.DataFrame(lista_posizioni)

    # Calcolo della media matematica delle posizioni per ogni istante e per squadra
    centroidi = df.groupby(["timestamp", "team"])[["x", "y"]].mean().reset_index()
    centroidi.columns = ["timestamp", "team", "centroide_x", "centroide_y"]

    print("\n--- Coordinate del Baricentro Squadre (Primi 10 Frame) ---")
    print(centroidi.head(10))

except FileNotFoundError:
    print("Errore: Python non trova il file di tracking.")