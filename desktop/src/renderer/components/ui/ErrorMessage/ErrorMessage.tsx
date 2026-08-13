import "./ErrorMessage.css";
import type { ErrorMessageProps } from "../../../models/ui/ErrorMessageProps";

export default function ErrorMessage({ message, className = "", style }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      className={`error-message ${className}`.trim()}
      style={style}
    >
      {message}
    </div>
  );
}
