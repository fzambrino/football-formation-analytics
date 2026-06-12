import os
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch


def visualizza_lavagnetta_ungherese(
        nome_team, team_code, testo_fase, modulo, centri_ruoli, labels_reparti, nome_script="generico"
):
    """
    Disegna la lavagnetta tattica del modulo usando mplsoccer, ereditando lo sfondo
    verde scuro (stile Opta/Satellitare radar) dello script di test.
    Include le linee di reparto connesse nativamente e salva il file PNG in out/nome_script/.
    Il nome_script è dato dal file chiamante.
    """
    # Configurazione Colori
    COLOR_SFONDO = '#22312b'  # Verde scuro opaco
    COLOR_LINEE = '#c7d5cc'   # Bianco ghiaccio/grigio soft per le linee del campo

    # Inizializza il campo
    pitch = Pitch(pitch_type='opta', pitch_color=COLOR_SFONDO, line_color=COLOR_LINEE, linewidth=1.5)

    # Genera la figura e l'asse tramite mplsoccer
    fig, ax = pitch.draw(figsize=(11, 7))
    fig.patch.set_facecolor(COLOR_SFONDO)

    # 1. Calcolia le coordinate dei giocatori mappate sul sistema di riferimento Opta
    x_campo = ((centri_ruoli[:, 0] / 105.0) + 0.5) * 100.0
    y_campo = ((centri_ruoli[:, 1] / 68.0) + 0.5) * 100.0

    # Blocco di connessione tra reparti
    n_reparti = len(np.unique(labels_reparti))

    # Raggruppa le coordinate (x, y) associate a ciascun indice di reparto
    reparti_coords = {r: [] for r in range(n_reparti)}
    for idx, (x, y) in enumerate(zip(x_campo, y_campo)):
        reparti_coords[labels_reparti[idx]].append((x, y))

    # Per ogni reparto, ordina i nodi per l'asse Y (da un fallo laterale all'altro)
    for r in range(n_reparti):
        coords_reparto = reparti_coords[r]
        if len(coords_reparto) > 1:
            # Ordina in base alla coordinata Y per evitare incroci a zig-zag
            coords_reparto.sort(key=lambda coord: coord[1])
            x_values, y_values = zip(*coords_reparto)

            # Usa pitch.plot anziché ax.plot per allinearlo al sistema mplsoccer
            pitch.plot(
                x_values, y_values,
                ax=ax,
                color="#ffffff",
                alpha=0.35,
                linewidth=2.0,
                linestyle="-",
                zorder=3
            )

    # Posizionamento dei nodi dei giocatori
    # Identificazione cromatica (H rosso acceso, A blu scuro)
    colore_maglia = "#e63946" if team_code == "H" else "#457b9d"
    colore_bordo = "#ffffff"

    # Disegna i nodi dei 10 giocatori
    ax.scatter(
        x_campo,
        y_campo,
        s=550,
        color=colore_maglia,
        edgecolors=colore_bordo,
        linewidths=2.0,
        zorder=5,
    )

    # Numerazione progressiva interna da 1 a 10 per i ruoli stabili
    for idx in range(10):
        ax.text(
            x_campo[idx],
            y_campo[idx],
            str(idx + 1),
            color="#ffffff",
            weight="bold",
            ha="center",
            va="center",
            fontsize=11,
            zorder=6,
        )

    # Titoli e styling
    ax.set_title(
        f"{nome_team} | Rilevazione Sistema: {modulo}\n{testo_fase}",
        fontsize=14,
        weight="bold",
        color=COLOR_LINEE,
        pad=12,
    )

    # Salva i risultati in out/geometricAnalysis/nome_script/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    radice_progetto = os.path.abspath(os.path.join(current_dir, "..", ".."))

    cartella_output = os.path.join(radice_progetto, "out", "geometricAnalysis",nome_script)
    os.makedirs(cartella_output, exist_ok=True)

    # Restiling del nome del file per l'esportazione
    nome_pulito_team = nome_team.replace(" ", "_").replace("-", "_")
    nome_pulito_fase = testo_fase.split(" (")[0].replace(" ", "_")
    nome_file = f"{nome_pulito_team}_{nome_pulito_fase}.png"
    percorso_salvataggio = os.path.join(cartella_output, nome_file)

    # Esportazione ad alta fedeltà con colore di sfondo forzato nativo
    plt.savefig(percorso_salvataggio, facecolor=fig.get_facecolor(), edgecolor='none', dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"       [GRAFICO OMNI] Lavagnetta salvata con successo in: {percorso_salvataggio}")