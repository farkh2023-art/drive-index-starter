# 📦 Drive Index Starter Pack

**Installation**
```bash
pip install -r requirements.txt
# drive-index-starter

Base de départ pour un projet d’indexation, d’audit et de traitement de contenu Google Drive, avec tests automatisés et intégration continue.

## Vue d’ensemble

`drive-index-starter` fournit une structure propre pour démarrer un projet orienté :

- indexation de contenus issus de Google Drive,
- extraction et traitement de données,
- audit ou visualisation des résultats,
- validation par tests unitaires et d’intégration,
- exécution automatique via CI.

L’objectif du dépôt est d’offrir une fondation simple, testable et extensible pour construire un pipeline fiable autour de documents ou fichiers issus de Google Drive.

## Objectifs du projet

Ce dépôt a été pensé pour :

- accélérer le démarrage d’un projet d’indexation documentaire ;
- structurer le code autour d’extracteurs, tests et pipeline ;
- faciliter l’ajout de traitements IA ou analytiques ;
- sécuriser les évolutions grâce à une chaîne CI.

## Fonctionnalités

- structure de projet prête à étendre ;
- base de tests avec `pytest` ;
- tests unitaires, d’intégration et de pipeline ;
- workflow GitHub Actions pour validation automatique ;
- support d’un audit ou d’une visualisation HTML ;
- organisation adaptée à une évolution progressive vers un pipeline plus complet.

## Structure du dépôt

```text
drive-index-starter/
├── google-drive-audit.html
├── tests/
│   ├── conftest.py
│   ├── test_extractors.py
│   ├── test_ia.py
│   ├── test_integration.py
│   └── test_pipeline.py
├── .github/
│   └── workflows/
├── ...
m
