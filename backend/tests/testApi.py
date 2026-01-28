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

    def test_auth_status_not_authenticated(self):
        """Test endpoint /auth/status sans authentification."""
        response = self.client.get("/auth/status")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("is_authenticated", data)

    def test_logout_without_session(self):
        """Test endpoint /auth/logout sans session active."""
        response = self.client.post("/auth/logout")

        # Devrait réussir même sans session
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
