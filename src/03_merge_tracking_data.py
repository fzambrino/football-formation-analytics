import json
import os
import glob
import pandas as pd

# 1. Definiamo i percorsi dinamici
script_dir = os.path.dirname(os.path.abspath(__file__))
cartella_tracking = os.path.abspath(os.path.join(script_dir, "..", "data", "raw", "tracking"))
cartella_output = os.path.abspath(os.path.join(script_dir, "..", "data", "processed"))

# Creiamo la cartella 'processed' se non esiste ancora
os.makedirs(cartella_output, exist_ok=True)

print("--- Pipeline Sports Analytics: Unione File Tracking (98 blocchi) ---")

# 2. Troviamo tutti i file json che iniziano con 'output' nella cartella
file_json = glob.glob(os.path.join(cartella_tracking, "output*.json"))

# Ordiniamo i file per numero (da output0 a output97) altrimenti Python li legge alla rinfusa
file_json.sort(key=lambda x: int(os.path.basename(x).replace("output", "").replace(".json", "")))

print(f"Trovati {len(file_json)} file di tracking da unire.")

lista_tutti_i_frame = []
conteggio_file = 0

# 3. Inizia il super-ciclo di lettura
for percorso_file in file_json:
    nome_file = os.path.basename(percorso_file)

    with open(percorso_file, "r", encoding="utf-8") as f:
        dati_blocco = json.load(f)

    for frame in dati_blocco:
        timestamp = frame["matchtimestamp"]
        for giocatore in frame["players"]:
            if giocatore["role"] != "g":  # Escludiamo sempre i portieri per il baricentro
                lista_tutti_i_frame.append({
                    "timestamp": timestamp,
                    "team": giocatore["team"],
                    "player_id": giocatore["id"],
                    "jersey": giocatore["jerseyNumber"],
                    "x": giocatore["x"],
                    "y": giocatore["y"]
                })

    conteggio_file += 1
    # Stampiamo un feedback ogni 10 file per vedere che il computer sta lavorando e non è bloccato
    if conteggio_file % 10 == 0:
        print(f"Progresso: {conteggio_file}/{len(file_json)} file letti con successo...")

print("\nEstrazione completata! Creazione del database in corso (conversione in Pandas)...")

# 4. Trasformiamo la mega-lista in un unico DataFrame gigante
df_completo = pd.DataFrame(lista_tutti_i_frame)

print(f"Database creato! Righe totali generate: {len(df_completo)}")

# 5. Salviamo il risultato in un file compresso super leggero (.parquet invece di .csv)
# Il formato Parquet è perfetto per la tesi perché pesa 10 volte meno di un file Excel o CSV
file_salvato = os.path.join(cartella_output, "integrated_tracking_data.parquet")
df_completo.to_parquet(file_salvato, index=False)

print(f"✅ Successo! Il mega-database di tutta la partita è stato salvato in:\n--> {file_salvato}")