# NadIA

## Description

NadIA est une assistante virtuelle alimentée par une IA locale (type LLaMA) pour aider à gérer les emails de manière sécurisée et productive. Elle peut connecter des boîtes mail (Gmail d’abord), résumer les messages, proposer des réponses, classer/archiver les emails et identifier les plus importants, le tout sans envoyer de données à l’extérieur (l’IA fonctionne en local).

L’application est **autonome** et fonctionne localement :

- interface desktop Electron + React
- backend Python embarqué
- aucune dépendance externe à lancer manuellement

---

## Architecture (vue simple)

```plaintext
+------------------+        +------------------+        +------------------+
|   Interface      | <----> |    Backend       | <----> |   Modèles LLM     |
|   Electron +     |        |   FastAPI +      |        |   LLaMA local     |
|   React          |        |   Python         |        |                  |
+------------------+        +------------------+        +------------------+
```

Le backend est **démarré automatiquement** par Electron.

---

## Technologies

- Desktop : Electron
- Frontend : React + TypeScript + Vite
- Backend : Python + FastAPI
- Build : Electron Builder

---

## Getting started (DEV)

### Prérequis

- NodeJS >= 18
- npm
- Python 3.10+ installé sur la machine

---

### Installation

```bash
cd desktop
npm install
```

### Initialisation backend (une seule fois)

Lors du premier setup du projet, il est nécessaire d’initialiser l’environnement Python :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Lancement en mode DEV

```bash
cd desktop
npm run dev
```

L’application desktop devrait se lancer automatiquement.
