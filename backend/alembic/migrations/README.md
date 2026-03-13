## Stockage SQLite des emails

- **Adapter** : `backend.adapters.BDDProvider.sqlLite.SqliteStorageAdapter`
- **Emplacement par défaut** : `~/.nadia/emails.db` (défini par `storage_settings.DATA_DIR`)
- **Schéma** : modèles SQLAlchemy dans `backend.adapters.BDDProvider.sqlLite.models`

L’application crée et met à jour la base automatiquement au démarrage (via `SqliteStorageAdapter`), il n’y a rien à faire manuellement pour un environnement de dev classique.

---

## Utiliser une base locale dédiée (dev / tests manuels)

1. Choisir un dossier de travail, par exemple :
   - `C:\temp\nadia-db` ou `/tmp/nadia-db`
2. Lancer un shell Python (ou un script) qui instancie l’adapter avec ce dossier :

```python
from pathlib import Path
from backend.adapters.bddProvider.sqlLite import SqliteStorageAdapter

storage = SqliteStorageAdapter(data_dir=Path(r"C:\temp\nadia-db"))
```

Ce dossier contiendra un fichier `emails.db` indépendant de la base utilisée par l’application.

---

## Migrations Alembic

Les migrations vivent dans :  
`backend/adapters/BDDProvider/sqlLite/alembic/`

### Créer une nouvelle migration

1. Activer le venv :

```bash
cd c:\Users\Alexa\NadIa\nadIA
.\venv\Scripts\Activate.ps1    # PowerShell
```

2. Aller dans le dossier Alembic :

```bash
cd backend/adapters/bddProvider/sqlLite
```

3. Générer une migration à partir des modèles :

```bash
alembic revision --autogenerate -m "description"
```

4. Appliquer la migration sur la base par défaut :

```bash
alembic upgrade head
```

Par défaut, Alembic utilise `storage_settings.DATA_DIR / "emails.db"` (voir `alembic/env.py`).

