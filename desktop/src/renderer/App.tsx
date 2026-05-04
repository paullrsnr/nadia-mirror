import { NavLink, Outlet } from "react-router-dom";
import { colors, spacing } from "./theme";

const navLinkStyle = ({ isActive }: { isActive: boolean }): React.CSSProperties => ({
  marginRight: spacing.md,
  fontWeight: isActive ? "bold" : "normal",
  textDecoration: "none",
  color: isActive ? colors.buttonPrimary : colors.textPrimary,
  cursor: "pointer",
  background: "none",
  border: "none",
  fontSize: "14px",
  padding: `${spacing.sm}px ${spacing.card}px`,
  borderRadius: 3,
  backgroundColor: isActive ? "#e8f0fe" : "transparent",
});

export default function App() {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <nav
        style={{
          padding: `${spacing.sm}px ${spacing.page}px`,
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
      </nav>

      <main style={{ flex: 1, overflow: "hidden" }}>
        <Outlet />
      </main>
    </div>
  );
}
