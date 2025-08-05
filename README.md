# athlog

**athlog** est un petit projet perso pour planifier mes blocs d’entraînement et analyser mes séances Garmin localement, sans avoir à payer un abonnement à TrainingPeaks ou consorts.

L'objectif principal est d'automatiser :
- le renommage des fichiers `.fit` avec un nom explicite basé sur la séance,
- l’analyse de la répartition 80/20 (easy vs intense) sur la semaine,
- la génération automatique d’un rapport hebdomadaire `.txt`.
- ...

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

### 1. Renommer les fichiers `.fit` :

```bash
python fit_utils.py
```

### 2. Générer un rapport :

```bash
./run_analyze.sh /chemin/vers/le/dossier/2025-W23
```

## Dépendances

- `pandas`
- `fitparse`
