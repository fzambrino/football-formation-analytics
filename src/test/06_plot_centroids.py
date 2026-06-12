import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# SCRIPT 06: TEST DI CALCOLO E RAPPRESENTAZIONE DEI CENTROIDI TATTICI MULTI-FRAME
# Questo script seleziona 5 fotogrammi distribuiti equamente lungo il match,
# applica la normalizzazione spaziale e calcola il baricentro geometrico (centroide)
# di ciascuna squadra, mostrandoli sul campo come stelle colorate.

def main():
    # Configurazione dei percorsi dei file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(script_dir, "..", "data", "processed", "integrated_tracking_data.parquet")
    output_dir = os.path.join(script_dir, "..", "out", "test", "centroid_test")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(parquet_path):
        print(f"Errore: Database non trovato al percorso {parquet_path}.")
        return

    print("Caricamento del database di tracking...")
    df = pd.read_parquet(parquet_path)

    print("Filtraggio delle coordinate vuote o non valide...")
    df_clean = df.dropna(subset=['x', 'y']).copy()

    # Conteggio dei giocatori per timestamp per individuare un fotogramma ad alta densità
    counts = df_clean.groupby('timestamp').size()
    max_players_found = counts.max()

    threshold = max(1, max_players_found - 2)
    valid_timestamps = counts[counts >= threshold].index.tolist()

    print(f"Total high-density frames available: {len(valid_timestamps)}")

    # Selezione multi-frame: Estrazione di 5 fotogrammi equidistanti nel match
    num_snapshots = 5
    indices = np.linspace(0, len(valid_timestamps) - 1, num_snapshots, dtype=int)
    target_timestamps = [valid_timestamps[i] for i in indices]

    # Configurazione delle dimensioni fisse del campo per la normalizzazione
    X_MIN, X_MAX = -52.5, 52.5
    Y_MIN, Y_MAX = -34.0, 34.0
    PITCH_LENGTH, PITCH_WIDTH = 105.0, 68.0

    # Elaborazione ciclica di ciascun fotogramma selezionato
    for idx, target_timestamp in enumerate(target_timestamps, start=1):
        print(f"\n[{idx}/{num_snapshots}] Processing timestamp: {target_timestamp}...")
        frame_df = df_clean[df_clean['timestamp'] == target_timestamp].copy()

        # Normalizzazione avanzata dei dati (Clamping + Min-Max scaling)
        x_clamped = np.clip(frame_df['x'], X_MIN, X_MAX)
        y_clamped = np.clip(frame_df['y'], Y_MIN, Y_MAX)

        frame_df['x_normalized'] = ((x_clamped - X_MIN) / (X_MAX - X_MIN)) * PITCH_LENGTH
        frame_df['y_normalized'] = ((y_clamped - Y_MIN) / (Y_MAX - Y_MIN)) * PITCH_WIDTH

        # Separazione delle due squadre (H e A)
        teams = frame_df['team'].unique()
        if len(teams) < 2:
            print(f"Attenzione: Impossibile trovare due squadre distinte per il timestamp {target_timestamp}. Salto il frame.")
            continue

        # Garantisce la corretta associazione dei tag: H = Casa, A = Ospite
        if 'H' in teams and 'A' in teams:
            team_h_name = 'H'
            team_a_name = 'A'
        else:
            team_h_name = teams[0]
            team_a_name = teams[1]

        team_h_df = frame_df[frame_df['team'] == team_h_name]
        team_a_df = frame_df[frame_df['team'] == team_a_name]

        # Calcolo matematico dei centroidi (Media delle coordinate)
        centroid_h_x = team_h_df['x_normalized'].mean()
        centroid_h_y = team_h_df['y_normalized'].mean()

        centroid_a_x = team_a_df['x_normalized'].mean()
        centroid_a_y = team_a_df['y_normalized'].mean()

        # Inizializzazione del rettangolo di gioco personalizzato
        pitch = Pitch(pitch_type='custom', pitch_length=PITCH_LENGTH, pitch_width=PITCH_WIDTH,
                      pitch_color='#22312b', line_color='#c7d5cc')
        fig, ax = pitch.draw(figsize=(13, 8))
        fig.patch.set_facecolor('#22312b')

        # Posizionamento dei giocatori (Cerchi in semitrasparenza)
        # Casa - H: Rosso
        pitch.scatter(team_h_df['x_normalized'], team_h_df['y_normalized'],
                      ax=ax, color='#e63946', edgecolors='#ffffff', s=120, linewidth=1.2, alpha=0.6)
        # Ospite - A: Blu
        pitch.scatter(team_a_df['x_normalized'], team_a_df['y_normalized'],
                      ax=ax, color='#457b9d', edgecolors='#ffffff', s=120, linewidth=1.2, alpha=0.6)

        # Posizionamento dei Centroidi (Grandi stelle opache)
        pitch.scatter(centroid_h_x, centroid_h_y, ax=ax, color='#e63946', edgecolors='#ffffff',
                      s=500, marker='*', linewidth=2, label=f'Centroide (Casa)')
        pitch.scatter(centroid_a_x, centroid_a_y, ax=ax, color='#457b9d', edgecolors='#ffffff',
                      s=500, marker='*', linewidth=2, label=f'Centroide (Ospite)')

        # Dettagli grafici ed estetici
        safe_timestamp = str(target_timestamp).replace(":", "-").replace(".", "-")
        ax.set_title(f"Istantanea Tattica {idx} - Centroide Squadre", color='#c7d5cc', fontsize=16, pad=10)
        ax.legend(facecolor='#22312b', edgecolor='#c7d5cc', labelcolor='#c7d5cc',
                  loc='upper left', handletextpad=1.0, labelspacing=1.2)

        # Salvataggio dell'immagine con denominazione incrementale
        output_file = os.path.join(output_dir, f"centroids_snapshot_{idx}_{safe_timestamp}.png")
        plt.savefig(output_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Immagine salvata correttamente: {output_file}")

    print("\nTutte le istantanee dei centroidi sono state generate con successo! Controlla la cartella 'out/centroid_test'.")

if __name__ == "__main__":
    main()