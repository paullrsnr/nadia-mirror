# Migrations du schéma SQLite

Les migrations sont exécutées **automatiquement au démarrage** (à l’ouverture de la BDD). Aucun script à lancer à la main.

## Ajouter une nouvelle migration

1. Créer un fichier dans `versions/` : `V00N_description_courte.py` (ex. `V002_add_read_status.py`).
2. Définir une fonction `up(conn: sqlite3.Connection) -> None` qui applique les changements (CREATE, ALTER, etc.).
3. Enregistrer la migration dans `runner.py` : ajouter le module dans la liste `_MIGRATIONS`.

Exemple :

```python
# versions/V002_add_read_status.py
import sqlite3

def up(conn: sqlite3.Connection) -> None:
    conn.execute("ALTER TABLE emails ADD COLUMN is_read INTEGER DEFAULT 0")
```

Dans `runner.py` :

```python
from backend.database.migrations.versions import V001_initial_schema, V002_add_read_status

_MIGRATIONS = [
    ("V001_initial_schema", V001_initial_schema.up),
    ("V002_add_read_status", V002_add_read_status.up),
]
```

Les BDD existantes sans table `schema_version` sont détectées (legacy) et mises à jour une fois avant d’appliquer les versions suivantes.
