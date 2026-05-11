import "./App.css";
import { NavLink, Outlet } from "react-router-dom";
import { useTheme } from "./hooks/useTheme";

export default function App() {
  const { theme, toggle } = useTheme();

  return (
    <div className="app-layout">
      <nav className="app-nav">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `app-nav__link${isActive ? " app-nav__link--active" : ""}`
          }
        >
          Boîte de réception
        </NavLink>
        <NavLink
          to="/models"
          className={({ isActive }) =>
            `app-nav__link${isActive ? " app-nav__link--active" : ""}`
          }
        >
          Modèles IA
        </NavLink>
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `app-nav__link${isActive ? " app-nav__link--active" : ""}`
          }
        >
          Paramètres
        </NavLink>

        <button
          onClick={toggle}
          aria-label={theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"}
          className="app-nav__theme-toggle"
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </nav>

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
