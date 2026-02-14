# Base de données - SQLAlchemy & Alembic

Ce dossier contient toute la configuration de la base de données SQLite avec SQLAlchemy et les migrations gérées par Alembic.

## Structure

```
backend/database/
├── alembic/                    # Configuration et migrations Alembic
│   ├── versions/              # Scripts de migration
│   └── env.py                 # Configuration Alembic
├── models/                     # Modèles SQLAlchemy ORM
│   ├── base.py                # Classe de base DeclarativeBase
│   ├── emailModel.py          # Modèle Email
│   └── syncMetadataModel.py   # Modèle SyncMetadata
├── services/                   # Services de gestion de données
│   ├── emailRepository.py     # Repository pour opérations CRUD
│   └── sqliteStorage.py       # Facade SqliteStorage (compatibilité)
├── alembic.ini                # Configuration Alembic
├── session.py                 # Configuration session & engine
└── README.md                  # Ce fichier
```

## SQLAlchemy

### Modèles

Les modèles SQLAlchemy sont définis dans `models/` :
- `EmailModel` : Table `emails` pour stocker les emails synchronisés
- `SyncMetadataModel` : Table `sync_metadata` pour les timestamps de sync

### Session & Engine

La configuration de la session et de l'engine est dans `session.py` :

```python
from backend.database import init_engine, create_session, get_session

# Initialiser l'engine (fait automatiquement par SqliteStorage)
init_engine(db_path)

# Créer une session pour usage direct
session = create_session()
try:
    # ... opérations
finally:
    session.close()

# Ou utiliser get_session() comme dépendance FastAPI
@app.get("/emails")
def get_emails(session: Session = Depends(get_session)):
    # ...
```

### Repository

Le `EmailRepository` fournit des méthodes CRUD typées :

```python
from backend.database import EmailRepository, create_session

session = create_session()
repository = EmailRepository(session)

# Sauvegarder un email
repository.save_email(email, provider="gmail")

# Récupérer des emails
emails, total = repository.get_emails(max_results=50, offset=0)

# Sync time
last_sync = repository.get_last_sync_time()
repository.update_last_sync_time()

session.close()
```

## Alembic - Migrations

### Commandes courantes

**Toutes les commandes doivent être exécutées depuis `backend/database/`** :

```bash
cd backend/database

# Créer une nouvelle migration (auto-détection des changements)
alembic revision --autogenerate -m "description_du_changement"

# Appliquer toutes les migrations en attente
alembic upgrade head

# Annuler la dernière migration
alembic downgrade -1

# Voir l'état actuel
alembic current

# Voir l'historique des migrations
alembic history

# Downgrade vers une version spécifique
alembic downgrade <revision_id>
```

### Créer une migration

1. Modifier les modèles dans `models/`
2. Générer la migration automatiquement :
   ```bash
   alembic revision --autogenerate -m "add_new_column"
   ```
3. Vérifier le fichier généré dans `alembic/versions/`
4. Appliquer la migration :
   ```bash
   alembic upgrade head
   ```

### Migration initiale

Pour une nouvelle installation, la migration initiale crée les tables :

```bash
cd backend/database
alembic upgrade head
```

**Note** : `SqliteStorage.__init__()` crée automatiquement les tables si elles n'existent pas, donc cette étape est optionnelle pour une nouvelle installation. Cependant, pour les installations existantes, Alembic gère l'évolution du schéma.

### Configuration

La configuration Alembic est dans :
- `alembic.ini` : Configuration principale
- `alembic/env.py` : Script d'environnement qui :
  - Importe les modèles
  - Configure l'URL de la base de données dynamiquement
  - Active l'auto-génération des migrations

## Migration depuis l'ancien système

L'ancien système utilisait un `migrations/runner.py` custom. Ce fichier est maintenant déprécié et ne fait plus rien. Toutes les migrations sont gérées par Alembic.

### Pour les développeurs

Si vous avez une base de données existante avec l'ancien schéma :

1. Vos données sont préservées
2. Alembic détecte automatiquement les différences
3. La première migration appliquera les changements de schéma nécessaires

## Bonnes pratiques

1. **Toujours** vérifier les migrations auto-générées avant de les appliquer
2. **Tester** les migrations en local avant de les pousser
3. **Nommer** les migrations de manière descriptive
4. **Documenter** les changements complexes dans le fichier de migration
5. **Éviter** les changements destructifs sans plan de rollback
6. **Utiliser** `alembic upgrade head` pour appliquer toutes les migrations

## Dépannage

### Erreur "Target database is not up to date"

```bash
alembic upgrade head
```

### Erreur "Can't locate revision identified by 'xxxxx'"

Vérifier que toutes les migrations sont présentes dans `alembic/versions/`.

### Reset complet (ATTENTION : perte de données)

```bash
# Supprimer la base
rm ~/.nadia/emails.db

# Recréer avec les migrations
cd backend/database
alembic upgrade head
```
