import "./PageHeader.css";
import { Link } from "react-router-dom";
import type { PageHeaderProps } from "../../../models/ui";

export default function PageHeader({ title }: PageHeaderProps) {
  return (
    <header className="page-header">
      <Link to="/" className="page-header__back">
        ← Nadia
      </Link>
      <h1 className="page-header__title">{title}</h1>
    </header>
  );
}
