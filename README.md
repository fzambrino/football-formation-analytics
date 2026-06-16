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

Questo progetto nasce dall'esigenza di definire e classificare la formazione tattica di una squadra in tempo reale durante lo svolgimento di una partita di calcio. Superando i limiti delle definizioni tattiche rigide e statiche dei manuali, il framework analizza il posizionamento fluido dei calciatori interpretandolo come una rete spaziale continua.

Il sistema è strutturato in due macro-sezioni sequenziali:

---

### Sezione 1: Tracking e Computer Vision

Questa sezione introduce l'infrastruttura di visione artificiale sviluppata per tracciare visivamente il movimento dei calciatori all'interno della partita. Il modulo evidenzia un'evoluzione tecnologica divisa in due step incrementali:

#### 1.1 Infrastruttura Lineare (v1 - Soglia Colore HSV)
Un primo approccio basato su algoritmi tradizionali di Computer Vision:
* **Rilevamento base:** Sfrutta il modello `YOLOv8` standard per localizzare le persone sul terreno di gioco.
* **Classificazione cromatica:** Applica filtri di mascheramento basati sullo spazio colore **HSV** (*Hue, Saturation, Value*) per dividere i giocatori in base alla maglia (bianca o rossa) e individuare gli ufficiali di gara.
* **Limiti riscontrati:** Sebbene rapido, questo metodo risente fortemente dei cambi di luce, delle ombre sul campo e della sovrapposizione cromatica con lo staff a bordocampo.

#### 1.2 Infrastruttura Avanzata (v2 - YOLOv8 Custom & ByteTrack)
Un'evoluzione architetturale incentrata sul Deep Learning e l'ottimizzazione iterativa:
* **Modello personalizzato:** Implementazione di una pipeline basata su un modello **YOLOv8 Nano** addestrato su un dataset proprietario.
* **Persistenza temporale:** Integrazione con l'algoritmo **ByteTrack** per garantire la continuità degli identificativi degli atleti ed evitare scambi di ID durante i contrasti.
* **Ciclo di Active Learning:** Il dataset è stato raffinato iterativamente passando da 58 a 120 frame annotati su **Roboflow**. Attraverso lo studio analitico dei falsi positivi a runtime, le classi sono state ottimizzate escludendo lo staff a bordocampo e specializzando la rete neurale sulle reali maglie di gioco.

---

### Sezione 2: Analisi Tattica e Riconoscimento dei Moduli

Questa sezione estende e completa il framework. Per massimizzare la precisione analitica e validare il sistema, il modulo elabora i dati posizionali (integrando le metriche *Opta Vision* normalizzate) con l'obiettivo di scoprire, mappare e classificare la tattica fluida utilizzata da una squadra.

Il sistema si articola in due approcci complementari:

#### 2.1 La Soluzione Geometrico-Algoritmica
Un approccio guidato interamente dalla logica matematica e geometrica per la modellazione spaziale:
* **Spazializzazione dei Dati:** Acquisizione e normalizzazione delle coordinate cartesiane grezze $(x, y)$ dei giocatori di movimento per calcolarne la disposizione relativa.
* **Clustering Dinamico (I 10 Centroidi):** Attraverso gli algoritmi `K-Means` e `Agglomerative Clustering`, i flussi posizionali vengono raggruppati in 10 baricentri spaziali (centroidi) che fotografano i ruoli ideali occupati in quella specifica fase del match, senza forzarli in moduli rigidi.
* **Rilevamento Automatico dei Reparti:** In base alle distanze reciproche e alla profondità, il motore geometrico raggruppa i nodi nelle linee di *Difesa*, *Centrocampo*, *Trequarti* e *Attacco*, generando in tempo reale la stringa dinamica del modulo (es. `4-3-3` o `3-4-2-1`).

#### 2.2 La Soluzione basata su Machine Learning (Human-in-the-Loop)
Un sistema predittivo intelligente che eleva l'analisi geometrica integrandola con l'esperienza dell'operatore umano:
* **Interfaccia Grafica Interattiva:** Una dashboard tattica basata su `ipywidgets` e `mplsoccer` proietta a schermo i cluster calcolati per rendere visibili i reali flussi di gioco sul rettangolo verde.
* **Addestramento Guidato dall'Uomo:** Il match analyst interagisce a runtime con l'interfaccia per convalidare, modificare o correggere le proposte del motore geometrico, consolidando un dataset di *Ground Truth* (verità di fondo) ad altissima precisione.
* **Modellazione Predittiva:** Un classificatore **Random Forest** viene addestrato sulle decisioni storiche dell'esperto. Imparando dalle sfumature interpretate dall'occhio umano, il modello apprende a generalizzare, prevedendo in completa autonomia le formazioni su flussi di gioco totalmente inediti.

---

## Origine dei Dati

Per preservare la riservatezza dei dati e rispettare i vincoli di licenza aziendale, tutte le metriche sensibili relative a specifiche squadre, calciatori ed eventi di gara sono state rigorosamente anonimizzate e ricondotte a identificativi generici. Il framework elabora le informazioni combinando tre flussi di dati:

1. **Flusso Video Nativo (Sorgente di Visione Artificiale):** Il sistema acquisisce la registrazione video integrale del match. Questo feed video in chiaro costituisce il terreno di prova a runtime per la pipeline di Computer Vision. Da questa clip sono stati inoltre estratti e campionati i 120 frame eterogenei inseriti nell'infrastruttura di **Active Learning su Roboflow**, utilizzati per addestrare i livelli di localizzazione e tracciamento delle maglie di gioco e dei portieri tramite YOLOv8.
2. **Dati di Tracking Posizionale (Sorgente Commerciale):** Forniti da sistemi professionali di tracciamento ottico (**Opta Vision**). Il dataset raccoglie le coordinate bidimensionali cartesiane `(x, y)` dei 22 calciatori e del pallone frame per frame. Le posizioni sono state normalizzate nell'infrastruttura di pre-processing seguendo le dimensioni metriche regolamentari FIFA (Lunghezza: `[-52.5, 52.5]` metri; Larghezza: `[-34.0, 34.0]` metri).
3. **Dati d'Evento Pubblici (Sorgente Open-Source):** L'addestramento, il testing e la sincronizzazione temporale degli eventi si appoggiano al dataset pubblico di match-events [fypdata](https://www.kaggle.com/datasets/hashirhalaldeen/fypdata) disponibile sulla piattaforma **Kaggle**. Questo flusso fornisce la cronologia degli eventi di gara (posizioni, sostituzioni, ruoli, ...) fondamentale per l'unificazione e la persistenza degli ID di ruolo durante i cambi tattici (implementazione del paradigma *Human-in-the-Loop*).

---

## Architettura del Sistema

Il framework è progettato come una pipeline sequenziale e integrata, in cui i flussi video o posizionali vengono estratti, raffinati e trasformati in predizioni tattiche intelligenti:

1. **Il Modello Deep Learning & Tracking:** Riceve in ingresso il flusso video nativo, applica una maschera geometrica per escludere il rumore ambientale delle tribune e isola i calciatori e gli arbitri. Sfrutta l'architettura neurale **YOLOv8** per la localizzazione (*Detection*) e l'algoritmo **ByteTrack** per associare traiettorie e ID univoci continui ai soggetti sul campo.
2. **La Pipeline di Active Learning (L'Ottimizzazione):** Rappresenta il ciclo di feedback del sistema di visione artificiale. Attraverso il campionamento dei frame critici su **Roboflow**, il modello corregge iterativamente i propri errori (falsi positivi), escludendo lo staff a bordocampo e specializzando i pesi neurali sulle sole 5 classi analitiche di gioco (`AWAY`, `AWAY_GK`, `REF`, `HOME`, `HOME_GK`).
3. **Il Modello Geometrico (La Base Tattica):** Prende in carico i dati posizionali normalizzati (**Opta Vision**) e riduce la complessità spaziale dei 20 giocatori di movimento in 10 centroidi dinamici tramite algoritmi di clustering (`K-Means` / `Agglomerative`), calcolando una prima proposta matematica di modulo basata sulle profondità dei reparti.
4. **L'Interfaccia Grafica (La Validazione):** Rende visibili i cluster calcolati su una lavagnetta tattica interattiva (`mplsoccer` + `ipywidgets`). Questa postazione permette l'intervento del match analyst umano (*Human-in-the-Loop*) che convalida, supervisiona e corregge le anomalie, consolidando un dataset di *Ground Truth* (verità di fondo) ad altissima precisione.
5. **Il Modello ML (La Predizione Finale):** Un classificatore **Random Forest** si addestra sul dataset definitivo supervisionato dall'uomo. Il modello apprende direttamente dalle decisioni storiche dell'analista, acquisendo la capacità di riconoscere le fluttuazioni del calcio fluido e di prevedere in completa autonomia le formazioni su flussi di gioco totalmente inediti.

---

## Stack Tecnologico

Il progetto è sviluppato interamente in **Python** (v3.11) e si appoggia su un ecosistema solido di librerie specializzate, suddivise per moduli funzionali:

* **Computer Vision & Deep Learning (Tracking):**
  * `ultralytics`: Fornisce il framework nativo per l'architettura neurale **YOLOv8**, sfruttata sia per l'inferenza in tempo reale sul video che per il trasferimento dell'apprendimento (*Transfer Learning*) tramite l'addestramento custom convergente. Integra nativamente l'algoritmo **ByteTrack** per la persistenza temporale degli identificativi degli atleti.
  * `roboflow`: Utilizzata per l'integrazione e la sincronizzazione con l'infrastruttura cloud di Active Learning, gestendo il download automatico e sicuro dei dataset annotati.
  * `opencv-python`: Libreria fondamentale per il processamento video a basso livello; gestisce l'acquisizione dei frame dal file video, l'applicazione delle maschere geometriche per escludere il pubblico e il rendering grafico delle bounding box e dei testi in formato BGR.

* **Modellazione Geometrica & Machine Learning (Elaborazione Tattica):**
  * `scikit-learn`: Costituisce il core predittivo e di raggruppamento del sistema. Fornisce gli algoritmi di clustering non supervisionato (`K-Means` e `AgglomerativeClustering`) per la riduzione del campo a 10 centroidi e il classificatore supervisionato `Random Forest` per il riconoscimento autonomo dei moduli.
  * `numpy`: Utilizzato per il calcolo matematico e matriciale ad alte prestazioni, fondamentale per la normalizzazione geometrica delle coordinate cartesiane.

* **Data Engineering & Manipolazione Dati:**
  * `pandas`: Utilizzato per l'ingestione strutturata, la pulizia, il filtraggio basato sui tempi di possesso palla e la manipolazione delle serie storiche dei flussi di tracking.
  * `pyarrow`: Infrastruttura di back-end indispensabile per la lettura e la scrittura ultrarapida dei dataset posizionali ad alta intensità di memoria memorizzati in formato `Parquet`.

* **Interfaccia Grafica & Visualizzazione:**
  * `mplsoccer`: Libreria specializzata nell'analytics del calcio; utilizzata per il disegno standardizzato del rettangolo di gioco FIFA e la proiezione bidimensionale dei moduli tattici.
  * `matplotlib` & `seaborn`: Sfruttate per la generazione dei grafici statistici di supporto, istogrammi di distribuzione delle distanze e curve di densità dei reparti.
  * `ipywidgets` & `ipython`: Consentono la creazione dei componenti interattivi della lavagnetta tattica (slider temporali, bottoni di conferma e menu a tendina) integrati direttamente all'interno dei Jupyter Notebook per la validazione dell'operatore umano.

* **Ambiente di Sviluppo & Runtime Interattivo:**
  * `Jupyter Notebooks (.ipynb)`: I file di analisi principali (`solution1.ipynb` e `solution2.ipynb`) sono strutturati come quaderni interattivi. Questa tecnologia non viene usata come semplice blocco note, ma come una vera e propria **infrastruttura di runtime** che combina l'esecuzione sequenziale del codice, la visualizzazione immediata dei grafici tattici (`mplsoccer`) e l'interazione in tempo reale dell'utente con i widget.
  * `ipykernel`: Il motore di esecuzione (*kernel*) che fa girare il codice Python 3 all'interno dei notebook Jupyter, garantendo la persistenza delle variabili in memoria durante le sessioni interattive di validazione tattica.

* **Security & Environment Management:**
  * `python-dotenv`: Gestisce il caricamento sicuro e isolato delle chiavi private di Roboflow a runtime direttamente dal file locale `.env`, escludendo le credenziali dal tracciamento Git.

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

### 3. Configurazione delle Variabili d'Ambiente e Token Roboflow (Per il tracking)
Per consentire agli script di Visione Artificiale di comunicare in modo sicuro con Roboflow per reperire i frame già etichettati in maniera sicura e senza
esporre credenziali:
1. Crea un file di testo nella radice principale del progetto.
2. Rinominalo esattamente in `.env`
3. Inserisci al suo interno la tua chiave privata di sviluppo:
```bash
ROBOFLOW_API_KEY=chiave_fornita_da_Roboflow
```

### 4. Avvio dell'IDE e dei Notebook (Per l'analisi tattica)
IntelliJ gestisce l'ecosistema Jupyter in modo completamente automatizzato:
1. Naviga nella cartella `notebooks/` e apri uno dei file dei Notebook (un file `.ipynb`).
2. Clicca sul tasto **Run** (l'icona del Play) su una cella qualsiasi: IntelliJ rileverà l'ambiente,
installerà automaticamente i pacchetti Jupyter mancanti in background e avvierà il server locale sulla porta `8888`, eseguendo il codice all'istante

---

## Struttura del Progetto

```text 
football-formation-analytics/
├── analysis/                   # Notebook Jupyter
    ├── geometricalAnalysis     # Notebook Jupyter soluzione grafica 
    ├── MLAnalysis              # Notebook Jupyter soluzione basata sul Machine Learning 
    ├── test                    # File di test usati preliminarmente per testare il corretto funzionamento
    ├── .py                     # File utile al processamento dei dati
├── data/                       # Dataset di tracking posizionale e dati d'evento
├── out/                        # Cartella standardizzata per i grafici e gli output tattici
├── runs/                       # Contiene i pesi del modello YOLOv8 addestrato sul dataset di Roboflow
├── tracking/                   # Notebook Jupyter
    ├── v1                      # Contiene la versione di tracking basata su HSV
    ├── v2                      # Pipeline di Active Learning, download del dataset e modello YOLO custom
├── requirements.txt            # Dipendenze bloccate per la riproducibilità dell'ambiente
```
> ⚠️ **Nota sulla disponibilità delle cartelle:**
> * **`data/`**: la cartella **non è presente nel repository** in quanto i dataset di tracking posizionale e d'evento contengono dati commerciali protetti da accordi di riservatezza e file ad alta intensità di memoria (`.parquet`, `.json`, `.csv`) non idonei al versionamento Git. I flussi di dati devono essere allocati localmente prima di eseguire i notebook.
> * **`out/`**: la cartella **non è inclusa nella build iniziale** poiché viene generata automaticamente a runtime dagli script di elaborazione e rendering grafico per accogliere gli output tattici aggiornati.
> * **`runs/`**: la cartella è generata automaticamente dal framework Ultralytics durante le fasi di addestramento (training) e validazione del modello YOLOv8.

---

## Contesto e Autore

Questo progetto è stato interamente sviluppato da **Zambrino Francesco** come progetto formativo nell'ambito del tirocinio curriculare per il corso di Laurea Triennale in **Scienze e Tecnologie Informatiche (L-31)** presso l'**Università degli Studi di Salerno (UNISA)**, sede di Fisciano.

### Supervisione Accademica
Le attività di ricerca, progettazione software e validazione dei modelli sono state guidate e supervisionate dal **Prof. Luigi Di Biasi**, in qualità di Tutor Universitario e responsabile scientifico del progetto.

### Laboratorio di Ricerca
Le attività di sviluppo sperimentale e l'addestramento delle pipeline di Deep Learning sono state svolte presso il **cAIs Lab** (*Context-Aware Intelligent Systems Lab*), un laboratorio di eccellenza del Dipartimento di Informatica di UNISA, focalizzato sulla ricerca teorica e sull'applicazione pratica di tecnologie avanzate nell'ambito della **Computer Vision** e del **Machine Learning**.
