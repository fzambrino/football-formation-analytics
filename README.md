# Football Formation Analytics

## Indice
* [Panoramica del Progetto](#panoramica-del-progetto)
* [Origine dei Dati](#origine-dei-dati)
* [Architettura del Sistema](#architettura-del-sistema)
* [Stack Tecnologico](#stack-tecnologico)
* [Guida alla Configurazione](#guida-alla-configurazione)
* [Struttura del Progetto](#struttura-del-progetto)
* [Contesto e Autore](#contesto-e-autore)

---

## Panoramica del Progetto

Questo progetto nasce dall'esigenza di definire e classificare la formazione tattica di una squadra in tempo reale durante lo svolgimento di una partita di calcio.
Superando i limiti delle definizioni tattiche rigide e statiche dei manuali, il framework analizza il posizionamento fluido dei calciatori interpretandolo come
una rete spaziale continua.

Il sistema si basa essenzialmente in due sezioni:

### Sezione 1: La Soluzione Geometrica
La prima parte del progetto è interamente algoritmica e guidata dalla logica matematica. Mappa le posizioni dei giocatori come nodi
spaziali dinamici su una lavagnetta digitale personalizzata, costruita appositamente per la visualizzazione.

* **Spazializzazione dei Dati:** Ingesta le coordinate grezze di tracking $(x, y)$ dei giocatori di movimento e calcola la loro disposizione
relativa sul terreno di gioco.
* **Clustering Dinamico (I 10 Centroidi):** Invece di cercare un "4-4-2" prestabilito, l'algoritmo raggruppa i dati posizionali in 10 baricentri
spaziali (i ruoli ideali occupati in quella fase del match) e ne misura la profondità orizzontale.
* **Rilevamento Automatico dei Reparti:** Sulla base delle distanze reciproche e della posizione sull'asse della profondità del campo, il motore
geometrico raggruppa autonomamente i nodi nei tre reparti classici (Difesa, Centrocampo, Attacco), generando una stringa del modulo di partenza
(es. `4-3-3`, `3-4-2-1` o moduli asimmetrici del calcio fluido).

### Sezione 2: La Soluzione basata su Machine Learning
La seconda eleva la base geometrica trasformandola in un sistema predittivo intelligente, guidato interamente dall'esperienza e dall'addestramento umano.

* **Interfaccia Grafica Interattiva:** Una lavagnetta tattica interattiva basata su `ipywidgets` e `mplsoccer` mostra a schermo i cluster geometrici calcolati
sul campo da gioco reale.
* **Addestramento Guidato dall'Uomo:** Un esperto di calcio (match analyst o allenatore) interagisce in tempo reale con l'interfaccia per convalidare,
modificare o correggere il modulo proposto dall'algoritmo geometrico. Questo processo genera un dataset di *Ground Truth* (verità di fondo) ad altissima
precisione.
* **Modellazione Predittiva:** Un classificatore **Random Forest** viene addestrato su questo dataset validato dall'uomo. Imparando dalle correzioni
dell'esperto, il modello di Machine Learning diventa capace di prevedere e riconoscere in automatico le formazioni su nuovi dati di partita mai visti prima.

---

## Origine dei Dati

Per preservare la riservatezza dei dati e rispettare i vincoli di licenza aziendale, tutte le metriche sensibili relative a specifiche squadre, calciatori ed eventi di gara sono state rigorosamente anonimizzate e ricondotte a identificativi generici. Il framework elabora le informazioni combinando due flussi di dati complementari:

1. **Dati di Tracking Posizionale (Sorgente Commerciale):** Forniti da sistemi professionali di tracciamento ottico (**Opta Vision**). Il dataset raccoglie le coordinate bidimensionali cartesiane `(x, y)` dei 22 calciatori e del pallone frame per frame. Le posizioni sono state normalizzate nell'infrastruttura di pre-processing seguendo le dimensioni metriche regolamentari FIFA (Lunghezza: `[-52.5, 52.5]` metri; Larghezza: `[-34.0, 34.0]` metri).
2. **Dati d'Evento Pubblici (Sorgente Open-Source):** L'addestramento, il testing e la sincronizzazione temporale degli eventi si appoggiano al dataset pubblico di match-events [fypdata](https://www.kaggle.com/datasets/hashirhalaldeen/fypdata) disponibile sulla piattaforma **Kaggle**. Questo flusso fornisce la cronologia degli eventi di gara (posizioni, sostituzioni, ruoli, ...) fondamentale per l'unificazione e la persistenza degli ID di ruolo durante i cambi tattici (implementazione del paradigma *Human-in-the-Loop*).

---

## Architettura del Sistema

Il framework è progettato come una pipeline sequenziale in cui l'output della componente geometrica diventa la base per l'apprendimento del modello predittivo:

1. **Il Modello Geometrico (La Base):** Estrae le metriche spaziali dai dati di tracking grezzi, riduce la complessità del campo a 10 centroidi dinamici
e calcola una prima proposta di modulo tattico basata su distanze e profondità.
2. **L'Interfaccia Grafica (La Validazione):** Rende visibili i cluster su una lavagnetta tattica, permettendo all'analista umano di
correggere le anomalie in tempo reale (*Human-in-the-Loop*) e consolidare un dataset di *Ground Truth* accurato.
3. **Il Modello ML (La Predizione):** Un classificatore *Random Forest* si addestra sul dataset geometrico validato dall'uomo, imparando dalle e
tichette dell'analista per prevedere in autonomia le formazioni su nuovi dati di gioco.
Il modello apprende direttamente dalle etichette fornite dall'analista, acquisendo la capacità di riconoscere le fluttuazioni del calcio fluido 
e di prevedere in autonomia le formazioni su nuovi dati di gioco.

---

## Stack Tecnologico

Il progetto è sviluppato in **Python** e si appoggia sul seguente ecosistema di librerie:
* **Modellazione Geometrica e ML:** `scikit-learn` (per gli algoritmi di Clustering K-Means, Agglomerative e il classificatore Random Forest)
e `numpy` per il calcolo matriciale.
* **Manipolazione Dati:** `pandas` (per l'ingestione, la pulizia e la strutturazione delle serie storiche dei dati di tracking).
* **Interfaccia e Visualizzazione:** `mplsoccer` (per il rendering del campo da gioco e della lavagnetta tattica), `matplotlib` per i
grafici e `ipywidgets` per i componenti interattivi dell'interfaccia *Human-in-the-Loop*.

---

## Guida alla Configurazione

Segui questi passaggi per replicare l'ambiente virtuale e avviare il progetto sul tuo computer tramite terminale (PowerShell o Prompt dei comandi):

### 1. Creazione e attivazione dell'Ambiente Virtuale
Se non lo hai fatto durante la creazione del progetto nell'IDE, apri il terminale e crea un ambiente isolato con Python 3.11:
```bash
conda create --name <nome_ambiente> python=<versione_python> -y
conda activate <nome_ambiente>
```

### 2. Installazione delle Dipendenze
Installa tutte le librerie dello stack tecnologico (Scikit-Learn, Pandas, Mplsoccer, ecc.) sfruttando il file dei requisiti:
```bash
pip install -r requirements.txt
```

### 3. Avvio dell'IDE e dei Notebook
IntelliJ gestisce l'ecosistema Jupyter in modo completamente automatizzato:
1. Naviga nella cartella `notebooks/` e apri uno dei file dei Notebook (un file `.ipynb`).
2. Clicca sul tasto **Run** (l'icona del Play) su una cella qualsiasi: IntelliJ rileverà l'ambiente,
installerà automaticamente i pacchetti Jupyter mancanti in background e avvierà il server locale sulla porta `8888`, eseguendo il codice all'istante

---

## Struttura del Progetto

```text 
football-formation-analytics/
├── data/                       # Dataset di tracking posizionale e dati d'evento
├── out/                        # Cartella standardizzata per i grafici e gli output tattici
├── src/                        # Notebook Jupyter
    ├── geometricalAnalysis     # Notebook Jupyter soluzione grafica 
    ├── MLAnalysis              # Notebook Jupyter soluzione basata sul Machine Learning 
    ├── test                    # File di test usati preliminarmente per testare il corretto funzionamento
    ├── .py                     # File utile al processamento dei dati
├── requirements.txt            # Dipendenze bloccate per la riproducibilità dell'ambiente
└── README.md
```

---

## Contesto e Autore

Questo progetto è stato interamente sviluppato da **Zambrino Francesco** come progetto formativo nell'ambito del tirocinio per il corso
di Laurea Triennale in **Scienze e Tecnologie Informatiche  (L-31)** presso l'**Università degli Studi di Salerno (UNISA)**, sede di Fisciano.

### Laboratorio di Ricerca
Le attività di sviluppo e sperimentazione sono state svolte presso il **cAIs Lab** (Context-Aware Intelligent Systems Lab), 
un laboratorio di eccellenza focalizzato sulla ricerca e sull'applicazione di tecnologie avanzate nell'ambito della **Computer Vision** e del **Machine Learning**. 
