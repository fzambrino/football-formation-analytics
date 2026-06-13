import json
import os

# Comando utile a trovare la cartella di questo file (src)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Percorso per trovare il file .json in data/raw
percorso_file = os.path.abspath(os.path.join(script_dir, "..", "..", "data", "raw", "MA1_opta_match.json"))

print("--- Test di verifica ambiente e dati (Percorso Corretto) ---")
print(f"Sto cercando il file in:\n--> {percorso_file}\n")

if os.path.exists(percorso_file):
    with open(percorso_file, "r", encoding="utf-8") as f:
        dati = json.load(f)

    print("L'ambiente Conda e IntelliJ leggono i dati correttamente.")
    print(f"Descrizione Match: {dati['matchInfo']['description']}")
    print(f"Competizione: {dati['matchInfo']['competition']['name']}")
    print(f"Data Gara: {dati['matchInfo']['date']}")
else:
    print("Errore: Non riesco a trovare il file.")
