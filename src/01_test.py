import json
import os

# Questo comando trova la cartella esatta in cui si trova questo script (cioè 'src')
script_dir = os.path.dirname(os.path.abspath(__file__))

# Facciamo un passo indietro (..) per andare nella cartella principale del progetto, e poi entriamo in data/raw
percorso_file = os.path.abspath(os.path.join(script_dir, "..", "data", "raw", "MA1_opta_match.json"))

print("--- Test di verifica ambiente e dati (Percorso Corretto) ---")
print(f"Sto cercando il file in:\n--> {percorso_file}\n")

if os.path.exists(percorso_file):
    with open(percorso_file, "r", encoding="utf-8") as f:
        dati = json.load(f)

    print("✅ COMPLIMENTI! L'ambiente Conda e IntelliJ leggono i dati correttamente.")
    print(f"Descrizione Match: {dati['matchInfo']['description']}")
    print(f"Competizione: {dati['matchInfo']['competition']['name']}")
    print(f"Data Gara: {dati['matchInfo']['date']}")
else:
    print("❌ Errore: Non riesco ancora a trovare il file.")
    print("Controlla a sinistra in IntelliJ: la cartella 'data' deve essere una cartella principale, NON dentro 'src'!")
