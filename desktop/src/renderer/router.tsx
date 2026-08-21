import { createHashRouter } from "react-router-dom";
import App from "./App";
import InboxPage from "./pages/Inbox/InboxPage";
import SettingsPage from "./pages/Settings/SettingsPage";
import LlmsPage from "./pages/llms/LlmsPage";
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
      { path: "models", element: <LlmsPage /> },
      { path: "settings", element: <SettingsPage /> },
    ],
  },
]);
