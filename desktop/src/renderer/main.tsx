import React, { useState } from "react";
import ReactDOM from "react-dom/client";
import "./styles/global.css";
import Inbox from "./pages/Inbox";
import Settings from "./pages/Settings";
import AuthCallback from "./pages/AuthCallback";

function App() {
  const [currentPage, setCurrentPage] = useState<"inbox" | "settings">("inbox");

  return (
    <div>
      <nav style={{ padding: 10, borderBottom: "1px solid #ccc" }}>
        <button
          onClick={() => setCurrentPage("inbox")}
          style={{ marginRight: 10, fontWeight: currentPage === "inbox" ? "bold" : "normal" }}
        >
          📬 Boîte de réception
        </button>
        <button
          onClick={() => setCurrentPage("settings")}
          style={{ fontWeight: currentPage === "settings" ? "bold" : "normal" }}
        >
          ⚙️ Paramètres
        </button>
      </nav>
      {currentPage === "inbox" ? <Inbox /> : <Settings />}
    </div>
  );
}

const rootElement = document.getElementById("root");
if (!rootElement) {
  throw new Error("Root element not found");
}
const root = ReactDOM.createRoot(rootElement);

// Page de callback OAuth (redirection backend → frontend)
const isAuthCallback = window.location.pathname === "/auth/callback";

root.render(
  <React.StrictMode>
    {isAuthCallback ? <AuthCallback /> : <App />}
  </React.StrictMode>
);
