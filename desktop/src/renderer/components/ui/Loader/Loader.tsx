import "./Loader.css";
import type { LoaderProps } from "../../../models/ui/LoaderProps";

export default function Loader({ size = 32, label, fullPage = false }: LoaderProps) {
  const borderWidth = size >= 48 ? 4 : 3;

  const spinner = (
    <div
      className="loader-spinner"
      style={{ width: size, height: size, borderWidth }}
      role="status"
      aria-label={label ?? "Chargement..."}
    />
  );

  if (fullPage) {
    return (
      <div className="loader-fullpage">
        {spinner}
        {label && <p className="loader__label">{label}</p>}
      </div>
    );
  }

  return (
    <div className="loader-inline">
      {spinner}
      {label && <span className="loader__label">{label}</span>}
    </div>
  );
}
