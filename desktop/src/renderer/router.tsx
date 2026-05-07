import { createHashRouter } from "react-router-dom";
import App from "./App";
import Inbox from "./pages/inbox";
import Settings from "./pages/settings";
import Models from "./pages/Models/ModelsPage";
import AuthCallback from "./pages/authCallback";

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
    element: <AuthCallback />,
  },
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <Inbox /> },
      { path: "models", element: <Models /> },
      { path: "settings", element: <Settings /> },
    ],
  },
]);
