import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# SCRIPT 08: ESTRAZIONE DINAMICA DELLE LINEE DI REPARTO E LUNGHEZZA SQUADRA
# Questo script ordina geometricamente i giocatori per altezza campo (X) per
# identificare i reparti (Difesa, Centrocampo, Attacco) in modo agnostico.
# Calcola l'evoluzione temporale delle altezze dei reparti e la lunghezza del blocco.

def main():
    # Configurazione dei percorsi dei file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_path = os.path.join(script_dir, "..", "data", "processed", "integrated_tracking_data.parquet")
    output_dir = os.path.join(script_dir, "..", "out", "formation_analysis_meso")
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(parquet_path):
        print(f"Errore: Database non trovato al percorso {parquet_path}.")
        return

    print("Caricamento del database di tracking...")
    df = pd.read_parquet(parquet_path)

    print("Filtraggio delle coordinate vuote o non valide...")
    df_clean = df.dropna(subset=['x', 'y']).copy()

    # Normalizzazione standard (Clamping + Min-Max scaling)
    X_MIN, X_MAX = -52.5, 52.5
    PITCH_LENGTH = 105.0
    x_clamped = np.clip(df_clean['x'], X_MIN, X_MAX)
    df_clean['x_normalized'] = ((x_clamped - X_MIN) / (X_MAX - X_MIN)) * PITCH_LENGTH

    # Individuazione del punto di split (cambio campo fine primo tempo)
    unique_timestamps = sorted(df_clean['timestamp'].unique())
    ts_diffs = np.diff(unique_timestamps)
    max_diff_idx = np.argmax(ts_diffs)
    half_time_split_ts = unique_timestamps[max_diff_idx]

    # Calcolo dell'altezza tattica effettiva (distanza dalla propria porta)
    df_clean['altezza_tattica'] = 0.0
    primo_tempo = df_clean['timestamp'] <= half_time_split_ts
    secondo_tempo = df_clean['timestamp'] > half_time_split_ts

    # 1° Tempo: H difende a 0m, A difende a 105m
    df_clean.loc[primo_tempo & (df_clean['team'] == 'H'), 'altezza_tattica'] = df_clean['x_normalized']
    df_clean.loc[primo_tempo & (df_clean['team'] == 'A'), 'altezza_tattica'] = PITCH_LENGTH - df_clean['x_normalized']

    # 2° Tempo: Le porte si invertono
    df_clean.loc[secondo_tempo & (df_clean['team'] == 'H'), 'altezza_tattica'] = PITCH_LENGTH - df_clean['x_normalized']
    df_clean.loc[secondo_tempo & (df_clean['team'] == 'A'), 'altezza_tattica'] = df_clean['x_normalized']

    print("Estrazione geometrica dei reparti in parallelo vettoriale (Modalità Ultra-Fast)...")

    # Ordinia l'intero dataframe in un colpo solo per timestamp, squadra e altezza
    df_sorted = df_clean.sort_values(by=['timestamp', 'team', 'altezza_tattica'])

    # Crea un contatore progressivo per ogni giocatore dentro lo stesso frame (da 0 a N)
    df_sorted['player_rank'] = df_sorted.groupby(['timestamp', 'team']).cumcount()

    # Estre i tre reparti filtrando direttamente sui vettori degli indici geometrici (Assumendo i 10 di movimento)
    # Difesa: i primi 4 (rank 0, 1, 2, 3)
    difesa_agg = df_sorted[df_sorted['player_rank'] < 4].groupby(['timestamp', 'team'])['altezza_tattica'].mean().rename('difesa')

    # Centrocampo: i successivi 4 (rank 4, 5, 6, 7)
    centrocampo_agg = df_sorted[(df_sorted['player_rank'] >= 4) & (df_sorted['player_rank'] < 8)].groupby(['timestamp', 'team'])['altezza_tattica'].mean().rename('centrocampo')

    # Attacco: gli ultimi 2 (rank 8, 9)
    attacco_agg = df_sorted[(df_sorted['player_rank'] >= 8) & (df_sorted['player_rank'] < 10)].groupby(['timestamp', 'team'])['altezza_tattica'].mean().rename('attacco')

    # Unisce i vettori calcolati in un unico DataFrame pulito
    df_linee = pd.concat([difesa_agg, centrocampo_agg, attacco_agg], axis=1).reset_index()

    # Gestisce i rari casi di frame con meno di 10 giocatori compilando i buchi (NaN) con un fallback lineare bouno
    df_linee['difesa'] = df_linee['difesa'].ffill()
    df_linee['centrocampo'] = df_linee['centrocampo'].ffill()
    df_linee['attacco'] = df_linee['attacco'].ffill()

    # Calcola la lunghezza della squadra in modo istantaneo
    df_linee['lunghezza'] = df_linee['attacco'] - df_linee['difesa']

    # Crea un indice cronologico normalizzato su base 0-90 minuti
    timestamps_unici_linee = sorted(df_linee['timestamp'].unique())
    ts_to_minutes = {ts: (idx / len(timestamps_unici_linee)) * 90.0 for idx, ts in enumerate(timestamps_unici_linee)}
    df_linee['match_progress'] = df_linee['timestamp'].map(ts_to_minutes)

    # Separazione dei dati per le due entità anonime
    df_casa = df_linee[df_linee['team'] == 'H'].sort_values('match_progress')
    df_ospite = df_linee[df_linee['team'] == 'A'].sort_values('match_progress')

    # GRAFICO 1: EVOLUZIONE DEI REPARTI DELLA SQUADRA IN CASA (H)
    print("Generazione del grafico delle linee di reparto per la Squadra in Casa...")
    plt.figure(figsize=(15, 6), facecolor='#22312b')
    ax = plt.axes()
    ax.set_facecolor('#22312b')

    plt.plot(df_casa['match_progress'], df_casa['attacco'], color='#e63946', linestyle=':', label='Linea Offensiva', linewidth=1.2)
    plt.plot(df_casa['match_progress'], df_casa['centrocampo'], color='#e63946', linestyle='--', label='Linea di Centrocampo', linewidth=1.5)
    plt.plot(df_casa['match_progress'], df_casa['difesa'], color='#e63946', linestyle='-', label='Linea Difensiva', linewidth=2.0)

    # Styling asse (Tema Lavagna)
    ax.spines['bottom'].set_color('#c7d5cc')
    ax.spines['left'].set_color('#c7d5cc')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#c7d5cc', labelsize=11)
    ax.xaxis.label.set_color('#c7d5cc')
    ax.yaxis.label.set_color('#c7d5cc')
    plt.grid(color='#c7d5cc', linestyle='--', linewidth=0.5, alpha=0.15)

    plt.xlim(0, 90)
    plt.ylim(0, 105)
    plt.title("Evoluzione Dinamica delle Linee di Reparto - Squadra in Casa (H)", color='#c7d5cc', fontsize=16, pad=15)
    plt.xlabel("Tempo di Gioco (Minuti)", fontsize=12, labelpad=10)
    plt.ylabel("Altezza dei Reparti dalla propria Porta (Metri)", fontsize=12, labelpad=10)
    plt.legend(facecolor='#22312b', edgecolor='#c7d5cc', labelcolor='#c7d5cc', loc='upper left')

    output_file_casa = os.path.join(output_dir, "linee_reparto_squadra_casa.png")
    plt.savefig(output_file_casa, facecolor=plt.gcf().get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    # GRAFICO 2: CONFRONTO DELLA LUNGHEZZA DEL BLOCCO SQUADRA (COMPRESSIONE TATTICA)
    print("Generazione del grafico di confronto sulla lunghezza dei blocchi...")
    plt.figure(figsize=(15, 6), facecolor='#22312b')
    ax = plt.axes()
    ax.set_facecolor('#22312b')

    # Applica una media mobile soft (rolling window) per rendere il grafico delle serie temporali più leggibile ed elegante
    df_casa['lunghezza_smooth'] = df_casa['lunghezza'].rolling(window=100, min_periods=1, center=True).mean()
    df_ospite['lunghezza_smooth'] = df_ospite['lunghezza'].rolling(window=100, min_periods=1, center=True).mean()

    plt.plot(df_casa['match_progress'], df_casa['lunghezza_smooth'], color='#e63946', label='Blocco Squadra in Casa (H)', linewidth=1.8, alpha=0.9)
    plt.plot(df_ospite['match_progress'], df_ospite['lunghezza_smooth'], color='#457b9d', label='Blocco Squadra Ospite (A)', linewidth=1.5, alpha=0.85)

    ax.spines['bottom'].set_color('#c7d5cc')
    ax.spines['left'].set_color('#c7d5cc')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(colors='#c7d5cc', labelsize=11)
    ax.xaxis.label.set_color('#c7d5cc')
    ax.yaxis.label.set_color('#c7d5cc')
    plt.grid(color='#c7d5cc', linestyle='--', linewidth=0.5, alpha=0.15)

    plt.xlim(0, 90)
    plt.ylim(0, 60) # La lunghezza massima di una squadra corta/lunga oscilla solitamente tra 15 e 50 metri
    plt.title("Compressione Tattica - Distanza tra Linea Difensiva e Linea Offensiva (Lunghezza Squadra)", color='#c7d5cc', fontsize=16, pad=15)
    plt.xlabel("Tempo di Gioco (Minuti)", fontsize=12, labelpad=10)
    plt.ylabel("Estensione del Blocco Squadra (Metri)", fontsize=12, labelpad=10)
    plt.legend(facecolor='#22312b', edgecolor='#c7d5cc', labelcolor='#c7d5cc', loc='upper right')

    output_file_lunghezza = os.path.join(output_dir, "confronto_lunghezza_squadre.png")
    plt.savefig(output_file_lunghezza, facecolor=plt.gcf().get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Successo! Analisi completata.\nGrafici salvati in '{output_dir}':\n1. linee_reparto_squadra_casa.png\n2. confronto_lunghezza_squadre.png")

if __name__ == "__main__":
    main()