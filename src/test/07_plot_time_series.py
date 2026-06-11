import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# SCRIPT 07: TEST DI ANALISI DELLE SERIE TEMPORALI E INTERDIPENDENZA DEI CENTROIDI
# Questo script analizza l'evoluzione temporale dei centroidi delle due squadre lungo l'intero match (0-90 minuti).
# Integra una logica di "specchiamento della coordinata X" (Mirroring) per il secondo tempo,
# invertendo matematicamente i lati per correggere il cambio campo.
# Questo permette di ottenere una timeline simmetrica in cui una squadra mantiene
# visivamente la stessa direzione di attacco per tutta la durata del grafico,
# rendendo immediata l'analisi dell'interdipendenza tattica e del baricentro.

def main():
    # Configurazione dei percorsi dei file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(script_dir, "..", "data", "processed", "integrated_tracking_data.parquet")
    output_dir = os.path.join(script_dir, "..", "out", "test", "centroid_analysis_test")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(parquet_path):
        print(f"Errore: Database non trovato al percorso {parquet_path}.")
        return

    print("Caricamento del database di tracking...")
    df = pd.read_parquet(parquet_path)

    print("Filtraggio delle righe non valide o vuote...")
    df_clean = df.dropna(subset=['x', 'y']).copy()

    # Normalizzazione dei dati (Clamping + Min-Max scaling)
    print("Normalizzazione di tutte le coordinate di tracking...")
    X_MIN, X_MAX = -52.5, 52.5
    PITCH_LENGTH = 105.0

    x_clamped = np.clip(df_clean['x'], X_MIN, X_MAX)
    df_clean['x_normalized'] = ((x_clamped - X_MIN) / (X_MAX - X_MIN)) * PITCH_LENGTH

    # Individuazione del punto di split (cambio campo fine primo tempo)
    print("Analizzando timestamps per determinare la fine del primo tempo...")
    unique_timestamps = sorted(df_clean['timestamp'].unique())
    ts_diffs = np.diff(unique_timestamps)
    max_diff_idx = np.argmax(ts_diffs)
    half_time_split_ts = unique_timestamps[max_diff_idx]
    print(f"Fine primo tempo trovato! Split del timestamp: {half_time_split_ts}")

    # Specchia entrambe le squadre nel secondo tempo per mantenere costante la direzione di attacco
    second_half_mask = df_clean['timestamp'] > half_time_split_ts
    print("Applicando lo specchiamento delle cordinate per il secondo tempo...")
    df_clean.loc[second_half_mask, 'x_normalized'] = PITCH_LENGTH - df_clean.loc[second_half_mask, 'x_normalized']

    # Czalcolo della serie temporale del centroide
    print("Calcolo dei centroidi tattici per ogni istante di gioco...")
    centroid_series = df_clean.groupby(['timestamp', 'team'])['x_normalized'].mean().unstack()

    if centroid_series.shape[1] < 2:
        print("Errore: Non ho potuto trovare i dati per entrambe le squadre.")
        return

    team_names = centroid_series.columns.tolist()
    if 'A' in team_names and 'H' in team_names:
        team_h_name = 'H'
        team_a_name = 'A'
    else:
        team_h_name = team_names[0]
        team_a_name = team_names[1]

    # Converte i timestamp in minuti relativi del match (da 0 a 90)
    centroid_series = centroid_series.reset_index()
    centroid_series['match_progress'] = (centroid_series.index / len(centroid_series)) * 90.0

    # Generazione del grafico della serie temporale
    print("Generazione del grafico pulito dell'interdipendenza dei centroidi...")
    plt.figure(figsize=(15, 6), facecolor='#22312b')
    ax = plt.axes()
    ax.set_facecolor('#22312b')

    # Tracciamento delle linee per entrambe le squadre
    plt.plot(centroid_series['match_progress'], centroid_series[team_h_name],
             color='#e63946', label=f'Team {team_h_name}', linewidth=1.5, alpha=0.85)
    plt.plot(centroid_series['match_progress'], centroid_series[team_a_name],
             color='#457b9d', label=f'Team {team_a_name}', linewidth=1.5, alpha=0.85)

    # Stile degli assi (Stile Lavagna)
    ax.spines['bottom'].set_color('#c7d5cc')
    ax.spines['left'].set_color('#c7d5cc')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    ax.tick_params(colors='#c7d5cc', labelsize=11)
    ax.xaxis.label.set_color('#c7d5cc')
    ax.yaxis.label.set_color('#c7d5cc')

    plt.grid(color='#c7d5cc', linestyle='--', linewidth=0.5, alpha=0.15)

    # Impostazione dei confini tattici
    plt.xlim(0, 90)
    plt.ylim(0, 105)

    # Titoli, etichette e indicatori tattici espliciti
    plt.title("Interdipendenza dei Centroidi di Squadra (Timeline Simmetrica del Match)", color='#c7d5cc', fontsize=16, pad=15)
    plt.xlabel("Tempo di Gioco (Minuti)", fontsize=12, labelpad=10)
    plt.ylabel("Posizione sul Campo (Metri)", fontsize=12, labelpad=10)

    # Aggiunta di indicatori chiari su quale squadra difende quale lato in base alla baseline fissa
    plt.yticks([0, 52.5, 105],
               ['0m\n(Porta squadra H)', '52.5m\n(Linea di Metà Campo)', '105m\n(Porta squadra A)'])

    plt.legend(facecolor='#22312b', edgecolor='#c7d5cc', labelcolor='#c7d5cc', loc='upper left')

    # Salvataggio del grafico finale
    output_file = os.path.join(output_dir, "centroid_height_timeline.png")
    plt.savefig(output_file, facecolor=plt.gcf().get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Successo! Grafico dell'interdipendenza salvato in: {output_file}")

if __name__ == "__main__":
    main()