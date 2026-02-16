# pylint: disable=invalid-name
"""Tests unitaires pour les handlers (Auth et Credentials)."""
import unittest

from backend.config.AuthHandlers.authUrlHandler import AuthUrlHandler
from backend.config.AuthHandlers.callbackHandler import CallbackHandler
from backend.config.AuthHandlers.authStatusHandler import AuthStatusHandler
from backend.config.CredentialsHandlers.loadCredentialsHandler import LoadCredentialsHandler
from backend.config.CredentialsHandlers.saveCredentialsHandler import SaveCredentialsHandler
from backend.config.CredentialsHandlers.clearCredentialsHandler import ClearCredentialsHandler


class TestAuthHandlers(unittest.TestCase):
    """Tests pour les handlers d'authentification."""

    def test_auth_url_handler_has_two_members(self):
        """Vérifie que AuthUrlHandler a bien 2 membres distincts."""
        members = list(AuthUrlHandler)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, "GMAIL")
        self.assertEqual(members[1].name, "OUTLOOK")

    def test_auth_url_handler_gmail(self):
        """Vérifie que le handler Gmail est enregistré."""
        handler = AuthUrlHandler.get_handler("gmail")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_auth_url_handler_outlook(self):
        """Vérifie que le handler Outlook est enregistré."""
        handler = AuthUrlHandler.get_handler("outlook")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_auth_url_handler_invalid_provider(self):
        """Vérifie qu'un provider invalide retourne None."""
        handler = AuthUrlHandler.get_handler("invalid")
        self.assertIsNone(handler)

    def test_callback_handler_has_two_members(self):
        """Vérifie que CallbackHandler a bien 2 membres distincts."""
        members = list(CallbackHandler)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, "GMAIL")
        self.assertEqual(members[1].name, "OUTLOOK")

    def test_callback_handler_gmail(self):
        """Vérifie que le handler Gmail est enregistré."""
        handler = CallbackHandler.get_handler("gmail")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_callback_handler_outlook(self):
        """Vérifie que le handler Outlook est enregistré."""
        handler = CallbackHandler.get_handler("outlook")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_auth_status_handler_has_two_members(self):
        """Vérifie que AuthStatusHandler a bien 2 membres distincts."""
        members = list(AuthStatusHandler)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, "GMAIL")
        self.assertEqual(members[1].name, "OUTLOOK")

    def test_auth_status_handler_gmail(self):
        """Vérifie que le handler Gmail est enregistré."""
        handler = AuthStatusHandler.get_handler("gmail")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_auth_status_handler_outlook(self):
        """Vérifie que le handler Outlook est enregistré."""
        handler = AuthStatusHandler.get_handler("outlook")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))


class TestCredentialsHandlers(unittest.TestCase):
    """Tests pour les handlers de credentials."""

    def test_load_handler_has_two_members(self):
        """Vérifie que LoadCredentialsHandler a bien 2 membres distincts."""
        members = list(LoadCredentialsHandler)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, "GMAIL")
        self.assertEqual(members[1].name, "OUTLOOK")

    def test_load_handler_gmail(self):
        """Vérifie que le handler Gmail est enregistré."""
        handler = LoadCredentialsHandler.get_handler("gmail")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_load_handler_outlook(self):
        """Vérifie que le handler Outlook est enregistré."""
        handler = LoadCredentialsHandler.get_handler("outlook")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_load_handler_invalid_provider(self):
        """Vérifie qu'un provider invalide retourne None."""
        handler = LoadCredentialsHandler.get_handler("invalid")
        self.assertIsNone(handler)

    def test_save_handler_has_two_members(self):
        """Vérifie que SaveCredentialsHandler a bien 2 membres distincts."""
        members = list(SaveCredentialsHandler)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, "GMAIL")
        self.assertEqual(members[1].name, "OUTLOOK")

    def test_save_handler_gmail(self):
        """Vérifie que le handler Gmail est enregistré."""
        handler_info = SaveCredentialsHandler.get_handler("gmail")
        self.assertIsNotNone(handler_info)
        self.assertTrue(hasattr(handler_info, "save_func"))
        self.assertTrue(callable(handler_info.save_func))

    def test_save_handler_outlook(self):
        """Vérifie que le handler Outlook est enregistré."""
        handler_info = SaveCredentialsHandler.get_handler("outlook")
        self.assertIsNotNone(handler_info)
        self.assertTrue(hasattr(handler_info, "save_func"))
        self.assertTrue(callable(handler_info.save_func))

    def test_clear_handler_has_two_members(self):
        """Vérifie que ClearCredentialsHandler a bien 2 membres distincts."""
        members = list(ClearCredentialsHandler)
        self.assertEqual(len(members), 2)
        self.assertEqual(members[0].name, "GMAIL")
        self.assertEqual(members[1].name, "OUTLOOK")

    def test_clear_handler_gmail(self):
        """Vérifie que le handler Gmail est enregistré."""
        handler = ClearCredentialsHandler.get_handler("gmail")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))

    def test_clear_handler_outlook(self):
        """Vérifie que le handler Outlook est enregistré."""
        handler = ClearCredentialsHandler.get_handler("outlook")
        self.assertIsNotNone(handler)
        self.assertTrue(callable(handler))


if __name__ == "__main__":
    unittest.main()
