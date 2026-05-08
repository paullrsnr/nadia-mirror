import { createHashRouter } from "react-router-dom";
import App from "./App";
import InboxPage from "./pages/inbox/InboxPage";
import SettingsPage from "./pages/settings/SettingsPage";
import ModelsPage from "./pages/Models/ModelsPage";
import AuthCallbackPage from "./pages/authCallback/AuthCallbackPage";

/**
 * Hash router — compatible Electron (file:// protocol) et ouverture de popup OAuth.
 * Routes :
 *   #/           → Inbox
 *   #/models     → Modèles LLM
 *   #/settings   → Paramètres
 *   #/auth/callback → Callback OAuth (popup)
 */
export const router = createHashRouter([
  {
    path: "/auth/callback",
    element: <AuthCallbackPage />,
  },
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <InboxPage /> },
      { path: "models", element: <ModelsPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);
