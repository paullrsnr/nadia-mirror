# pylint: disable=invalid-name
"""Tests unitaires pour l'API FastAPI."""
import unittest
from fastapi.testclient import TestClient

from backend.api.main import app


class TestApiHealth(unittest.TestCase):
    """Tests pour les endpoints de base de l'API."""

    def setUp(self):
        """Initialisation du client de test."""
        self.client = TestClient(app)

    def test_health_endpoint(self):
        """Test endpoint /health."""
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_health_endpoint_method_not_allowed(self):
        """Test que POST sur /health retourne 405."""
        response = self.client.post("/health")

        self.assertEqual(response.status_code, 405)


class TestAuthEndpoints(unittest.TestCase):
    """Tests pour les endpoints d'authentification."""

    def setUp(self):
        """Initialisation du client de test."""
        self.client = TestClient(app)

    def test_auth_status_gmail(self):
        """Test endpoint /auth/status/gmail."""
        response = self.client.get("/auth/status/gmail")

        # Devrait retourner 200 même si non authentifié
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("is_authenticated", data)
        self.assertIsInstance(data["is_authenticated"], bool)

    def test_auth_status_outlook(self):
        """Test endpoint /auth/status/outlook."""
        response = self.client.get("/auth/status/outlook")

        # Devrait retourner 200 même si non authentifié
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("is_authenticated", data)
        self.assertIsInstance(data["is_authenticated"], bool)

    def test_auth_url_gmail(self):
        """Test endpoint /auth/url/gmail."""
        response = self.client.get("/auth/url/gmail?redirect_uri=http://localhost")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("auth_url", data)
        self.assertIsInstance(data["auth_url"], str)

    def test_auth_url_outlook(self):
        """Test endpoint /auth/url/outlook."""
        response = self.client.get("/auth/url/outlook?redirect_uri=http://localhost")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("auth_url", data)
        self.assertIsInstance(data["auth_url"], str)

    def test_auth_url_invalid_provider(self):
        """Test endpoint /auth/url avec un provider invalide."""
        response = self.client.get("/auth/url/invalid?redirect_uri=http://localhost")

        # Pour l'instant le handler invalide provoque une 500
        self.assertEqual(response.status_code, 500)


class TestEmailsEndpoints(unittest.TestCase):
    """Tests pour les endpoints d'emails."""

    def setUp(self):
        """Initialisation du client de test."""
        self.client = TestClient(app)

    def test_get_emails_endpoint_exists(self):
        """Test que l'endpoint /emails existe."""
        response = self.client.get("/emails/?provider=gmail&max_results=10")

        # L'endpoint devrait répondre (même si erreur de données)
        self.assertIn(response.status_code, [200, 500])

    def test_get_emails_invalid_max_results(self):
        """Test endpoint /emails avec max_results invalide."""
        response = self.client.get("/emails/?provider=gmail&max_results=-1")

        # Devrait retourner une erreur de validation
        self.assertEqual(response.status_code, 422)

    def test_get_emails_redirect(self):
        """Test que /emails redirige vers /emails/."""
        response = self.client.get("/emails?provider=gmail", follow_redirects=False)

        # FastAPI redirige automatiquement /emails vers /emails/
        self.assertEqual(response.status_code, 307)


if __name__ == "__main__":
    unittest.main()
