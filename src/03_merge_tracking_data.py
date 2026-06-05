import json
import os
import glob
import pandas as pd

# SCRIPT 03: MERGE DEI FILE DI TRACKING
# Questo script prende i singoli file di tracking e li utilizza per la definizione di un unico
# file .parque dal quale prendere le informazioni del match per processarle

# Configurazione dei percorsi dei file
script_dir = os.path.dirname(os.path.abspath(__file__))
cartella_tracking = os.path.abspath(os.path.join(script_dir, "..", "data", "raw", "tracking"))
cartella_output = os.path.abspath(os.path.join(script_dir, "..", "data", "processed"))

# Crea la cartella 'processed' se non esiste
os.makedirs(cartella_output, exist_ok=True)

print("--- Pipeline Sports Analytics: Unione File Tracking ---")

# Trova tutti i file json che iniziano con 'output' nella cartella
file_json = glob.glob(os.path.join(cartella_tracking, "output*.json"))

# Ordina i file per numero (da output0 a output97)
file_json.sort(key=lambda x: int(os.path.basename(x).replace("output", "").replace(".json", "")))

print(f"Trovati {len(file_json)} file di tracking da unire.")

lista_tutti_i_frame = []
conteggio_file = 0

# Inizia il ciclo di lettura
for percorso_file in file_json:
    nome_file = os.path.basename(percorso_file)

    with open(percorso_file, "r", encoding="utf-8") as f:
        dati_blocco = json.load(f)

    for frame in dati_blocco:
        timestamp = frame["matchtimestamp"]
        for giocatore in frame["players"]:
            if giocatore["role"] != "g":  # Esclude i portieri per il baricentro
                lista_tutti_i_frame.append({
                    "timestamp": timestamp,
                    "team": giocatore["team"],
                    "player_id": giocatore["id"],
                    "jersey": giocatore["jerseyNumber"],
                    "x": giocatore["x"],
                    "y": giocatore["y"]
                })

    conteggio_file += 1
    # Stampa un feedback ogni 10 file per la visualizzazione del progresso di calcolo
    if conteggio_file % 10 == 0:
        print(f"Progresso: {conteggio_file}/{len(file_json)} file letti con successo...")

print("\nEstrazione completata. Creazione del database in corso (conversione in Pandas)...")

# Trasforma la lista in un unico DataFrame
df_completo = pd.DataFrame(lista_tutti_i_frame)

print(f"Database creato! Righe totali generate: {len(df_completo)}")

# Salva il risultato in un file compresso leggero (.parquet)
file_salvato = os.path.join(cartella_output, "integrated_tracking_data.parquet")
df_completo.to_parquet(file_salvato, index=False)

print(f"Successo. Il database di tutta la partita è stato salvato in:\n--> {file_salvato}")