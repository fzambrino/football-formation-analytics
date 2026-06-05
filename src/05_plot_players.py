import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# SCRIPT 05: TEST DI POSIZIONAMENTO E NORMALIZZAZIONE DEI GIOCATORI SUL CAMPO
# Questo script seleziona un fotogramma ad alta densità dal database Parquet,
# applica la normalizzazione Min-Max con clamping alle coordinate spaziali e
# posiziona i giocatori delle due squadre sul terreno di gioco.

def main():
    # Configurazione dei percorsi dei file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(script_dir, "..", "data", "processed", "integrated_tracking_data.parquet")
    output_dir = os.path.join(script_dir, "..", "out", "snapshot_test")
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

    # Impostazione arbitraria dell'offset per spostare in avanti il match
    # (Es. 0 = Calcio d'inizio)
    frame_offset = 0

    # Evita di andare oltre la fine dei dati disponibili
    target_idx = min(len(valid_timestamps) - 1, frame_offset)
    target_timestamp = valid_timestamps[target_idx]

    print(f"Fischio d'inizio rilevato a timestamp: {valid_timestamps[0]}")
    print(f"Inquadratura impostata al frame index: {target_idx}")

    frame_df = df_clean[df_clean['timestamp'] == target_timestamp].copy()

    # Normalizzazione.
    # Definizione dei confini standard del campo con origine al centro (0,0)
    # Profondità: Minimo definito a -52.5 (linea di porta a sx) e massimo a 52.5 (linea di porta a dx). Totale 105 lunghezza del campo
    # Larghezza: Minimo definito a -34 e massimo a 34. Totale: 68 larghezza del campo
    X_MIN, X_MAX = -52.5, 52.5
    Y_MIN, Y_MAX = -34.0, 34.0
    PITCH_LENGTH, PITCH_WIDTH = 105.0, 68.0

    # Clamping dei valori per mantenere le azioni fuori campo strettamente sui bordi del terreno
    x_clamped = np.clip(frame_df['x'], X_MIN, X_MAX)
    y_clamped = np.clip(frame_df['y'], Y_MIN, Y_MAX)

    # Normalizzazione Min-Max per traslare la scala da 0 a 105 (X) e da 0 a 68 (Y)
    frame_df['x_normalized'] = ((x_clamped - X_MIN) / (X_MAX - X_MIN)) * PITCH_LENGTH
    frame_df['y_normalized'] = ((y_clamped - Y_MIN) / (Y_MAX - Y_MIN)) * PITCH_WIDTH

    # Separazione delle due squadre (A e H)
    teams = frame_df['team'].unique()
    if len(teams) < 2:
        print("Attenzione: Impossibile trovare due squadre distinte in questo fotogramma.")
        return

    # Forziamo l'associazione basata sull'identità reale: H = squadra in casa, A = squadra fuori casa
    if 'H' in teams and 'A' in teams:
        team_h_name = 'H'
        team_a_name = 'A'
    else:
        team_h_name = teams[0]
        team_a_name = teams[1]

    team_h_df = frame_df[frame_df['team'] == team_h_name]
    team_a_df = frame_df[frame_df['team'] == team_a_name]

    # Inizializzazione di un campo personalizzato standard (da 0 a 105 su X, da 0 a 68 su Y)
    pitch = Pitch(pitch_type='custom',
                  pitch_length=PITCH_LENGTH,
                  pitch_width=PITCH_WIDTH,
                  pitch_color='#22312b',
                  line_color='#c7d5cc')

    fig, ax = pitch.draw(figsize=(13, 8))
    fig.patch.set_facecolor('#22312b')

    # Posizionamento dei giocatori utilizzando le coordinate perfettamente normalizzate
    # Squadra H: pallini rossi (Casa)
    pitch.scatter(team_h_df['x_normalized'], team_h_df['y_normalized'],
                  ax=ax, color='#e63946', edgecolors='#ffffff',
                  s=150, linewidth=1.5, label=f'Squadra {team_h_name} (Casa)')

    # Squadra A: pallini blu (Ospite)
    pitch.scatter(team_a_df['x_normalized'], team_a_df['y_normalized'],
                  ax=ax, color='#457b9d', edgecolors='#ffffff',
                  s=150, linewidth=1.5, label=f'Squadra {team_a_name} (Ospite)')

    # Aggiunta dei dettagli tattici (Titolo e Legenda)
    safe_timestamp = str(target_timestamp).replace(":", "-").replace(".", "-")
    ax.set_title(f"Match Snapshot (Normalized) - Time: {target_timestamp}", color='#c7d5cc', fontsize=16, pad=10)
    ax.legend(facecolor='#22312b', edgecolor='#c7d5cc', labelcolor='#c7d5cc', loc='upper left')

    # Salvataggio della mappa tattica finale
    output_file = os.path.join(output_dir, f"match_snapshot_{safe_timestamp}.png")
    plt.savefig(output_file, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Successo! L'istantanea tattica perfetta è stata salvata in: {output_file}")

if __name__ == "__main__":
    main()