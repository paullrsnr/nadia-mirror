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
- Compte Google avec accès Gmail API
- (Optionnel) Modèle LLaMA 3 8B au format GGUF pour les fonctionnalités IA

---

### Installation

```bash
cd desktop
npm install
```

### Initialisation backend (une seule fois)

Lors du premier setup du projet, il est nécessaire d'initialiser l'environnement Python :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` dans le dossier `backend` à partir de `.env.example`
2. Configurez vos identifiants Gmail OAuth2 :
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un projet ou sélectionnez-en un
   - Activez l'API Gmail
   - Créez des identifiants OAuth2 (Application de bureau)
   - Ajoutez `http://localhost:3333/auth/callback` comme URI de redirection
   - Copiez le Client ID et Client Secret dans `.env`

3. (Optionnel) Configurez le modèle LLM :
   - Téléchargez LLaMA 3 8B au format GGUF
   - Spécifiez le chemin dans `.env` avec `LLM_MODEL_PATH`

## Lancement en mode DEV

```bash
cd desktop
npm run dev
```

L'application desktop devrait se lancer automatiquement.

## Fonctionnalités MVP (V1)

✅ **Connexion Gmail OAuth2** - Authentification sécurisée avec stockage local chiffré
✅ **Synchronisation des emails** - Récupération et stockage local des emails
✅ **Résumé automatique** - Génération de résumés via LLaMA 3 8B
✅ **Détection d'importance** - Calcul de score d'importance pour chaque email
✅ **Extraction d'éléments** - Identification des dates, personnes, actions requises
✅ **Détection du ton** - Analyse du ton (formel, informel, urgent, etc.)
✅ **Quick digest** - Résumé global de la boîte mail
✅ **Génération de réponses** - Création de réponses via IA
✅ **Archivage** - Possibilité d'archiver des emails
✅ **Interface desktop** - UI complète avec React + Electron
