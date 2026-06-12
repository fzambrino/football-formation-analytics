import os
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# SCRIPT 04: TEST DI DISEGNO DEL CAMPO DA CALCIO BASELINE
# Questo script funge da test isolato per verificare il corretto funzionamento
# della libreria 'mplsoccer' e la generazione dei percorsi di output.

def main():
    # Configurazione dei percorsi dei file
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Definisce la directory di output (out/). Se non esiste, la crea
    output_dir = os.path.join(script_dir, "..", "out", "test", "pitch_test")
    os.makedirs(output_dir, exist_ok=True)

    print("Disegnando il campo da calcio...")

    # Inizializza un campo da calcio standard (120x80 metri è lo standard di default per Opta)
    pitch = Pitch(pitch_type='opta', pitch_color='#22312b', line_color='#c7d5cc')

    # Crea la figura
    fig, ax = pitch.draw(figsize=(13, 8))

    # Set dello sfondo
    fig.patch.set_facecolor('#22312b')

    # Aggiunta del titolo
    ax.set_title("Tactical Pitch Baseline - Test", color='#c7d5cc', fontsize=18, pad=10)

    # Definizione titolo del file e della locazione
    output_file = os.path.join(output_dir, "tactical_pitch_baseline.png")
    plt.savefig(output_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Successo! L'immagine del campo da calcio è stata salvata in:: {output_file}")

if __name__ == "__main__":
    main()