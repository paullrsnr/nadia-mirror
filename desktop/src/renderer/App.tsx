import { NavLink, Outlet } from "react-router-dom";
import { colors, spacing, radius } from "./styles";
import { useTheme } from "./hooks/useTheme";

const navLinkStyle = ({ isActive }: { isActive: boolean }): React.CSSProperties => ({
  marginRight: spacing.md,
  fontWeight: isActive ? "bold" : "normal",
  textDecoration: "none",
  color: isActive ? colors.buttonPrimary : colors.textPrimary,
  cursor: "pointer",
  background: "none",
  border: "none",
  fontSize: "14px",
  padding: `${spacing.sm} ${spacing.card}`,
  borderRadius: radius.sm,
  backgroundColor: isActive ? colors.backgroundNavActive : "transparent",
});

export default function App() {
  const { theme, toggle } = useTheme();

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <nav
        style={{
          padding: `${spacing.sm} ${spacing.page}`,
          borderBottom: `1px solid ${colors.borderStrong}`,
          backgroundColor: colors.backgroundMuted,
          display: "flex",
          alignItems: "center",
          gap: spacing.xs,
          flexShrink: 0,
        }}
      >
        <NavLink to="/" end style={navLinkStyle}>
          Boîte de réception
        </NavLink>
        <NavLink to="/models" style={navLinkStyle}>
          Modèles IA
        </NavLink>
        <NavLink to="/settings" style={navLinkStyle}>
          Paramètres
        </NavLink>

        <button
          onClick={toggle}
          aria-label={theme === "dark" ? "Passer en mode clair" : "Passer en mode sombre"}
          style={{
            marginLeft: "auto",
            background: "none",
            border: `1px solid ${colors.border}`,
            borderRadius: radius.sm,
            cursor: "pointer",
            padding: `${spacing.xs} ${spacing.sm}`,
            color: colors.textSecondary,
            fontSize: "14px",
          }}
        >
          {theme === "dark" ? "☀" : "☾"}
        </button>
      </nav>

      <main style={{ flex: 1, overflow: "hidden" }}>
        <Outlet />
      </main>
    </div>
  );
}
