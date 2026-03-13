# Configuration de NadIA

## Configuration Gmail OAuth2

**Important** : Les identifiants OAuth2 sont configurés **une seule fois** pour toute l'application. 
Tous les utilisateurs partagent ces identifiants, mais chaque utilisateur s'authentifie avec 
son propre compte Google. Les utilisateurs n'ont **aucune configuration à faire**.

### Configuration pour les développeurs/éditeurs

Si vous distribuez l'application, vous devez configurer les identifiants OAuth2 une seule fois :

1. **Créer un projet Google Cloud**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un nouveau projet ou sélectionnez un projet existant

2. **Activer l'API Gmail**
   - Dans le menu, allez dans "APIs & Services" > "Library"
   - Recherchez "Gmail API"
   - Cliquez sur "Enable"

3. **Créer des identifiants OAuth2**
   - Allez dans "APIs & Services" > "Credentials"
   - Cliquez sur "Create Credentials" > "OAuth client ID"
   - Si c'est la première fois, configurez l'écran de consentement OAuth
   - Sélectionnez "Desktop app" comme type d'application
   - Donnez un nom à votre application (ex: "NadIA")
   - Cliquez sur "Create"
   - **Copiez le Client ID et le Client Secret**

4. **Configurer l'URI de redirection**
   - Dans les identifiants créés, ajoutez l'URI de redirection autorisée :
     ```
     http://localhost:3333/auth/callback
     ```
   - Pour la production, ajoutez aussi l'URI de votre application

5. **Intégrer les identifiants dans l'application**
   - Dans le dossier `backend/`, créez un fichier `.env` (vous pouvez copier `env.example` comme base)
   - Ajoutez vos identifiants :
     ```env
     GMAIL_CLIENT_ID=votre_client_id_ici
     GMAIL_CLIENT_SECRET=votre_client_secret_ici
     GMAIL_REDIRECT_URI=http://localhost:3333/auth/callback
     ```
   - **Important** : 
     - Remplacez `votre_client_id_ici` et `votre_client_secret_ici` par vos vraies valeurs
     - Le fichier `.env` ne doit jamais être commité dans Git (déjà dans .gitignore)
     - Les valeurs par défaut dans `settings.py` sont vides, elles doivent être fournies via `.env`

### Pour les utilisateurs finaux

**Aucune configuration requise !** Les utilisateurs doivent simplement :
1. Lancer l'application
2. Cliquer sur "Se connecter à Gmail"
3. S'authentifier avec leur compte Google
4. Autoriser l'application à accéder à leur Gmail

C'est tout ! Chaque utilisateur utilise son propre compte, mais partage les identifiants OAuth2 de l'application.

