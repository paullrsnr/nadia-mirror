import "./SendToast.css";
import type { SendToastProps } from "../../models";

export default function SendToast({ subject, onCancel }: SendToastProps) {
  return (
    <div className="send-toast">
      <span className="send-toast__text">
        Envoi en cours{subject ? ` : ${subject}` : ""}...
      </span>
      <button type="button" className="send-toast__cancel" onClick={onCancel}>
        Annuler
      </button>
    </div>
  );
}
