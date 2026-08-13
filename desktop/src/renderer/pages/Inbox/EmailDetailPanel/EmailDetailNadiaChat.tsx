import "./EmailDetailNadiaChat.css";
import { useState } from "react";
import { IconSparkles, IconSend } from "../../../components/ui/icons";

export default function EmailDetailNadiaChat() {
  const [chatInput, setChatInput] = useState("");

  return (
    <div className="email-detail-nadia-chat">
      <div className="email-detail-nadia-chat__empty">
        <div className="email-detail-nadia-chat__icon">
          <IconSparkles />
        </div>
        <h3 className="email-detail-nadia-chat__title">Bonjour, je suis Nadia</h3>
        <p className="email-detail-nadia-chat__desc">
          Comment puis-je vous aider avec cet email ? Je peux le catégoriser, l'archiver ou vous
          proposer des réponses.
        </p>
      </div>
      <div className="email-detail-nadia-chat__input-row">
        <input
          type="text"
          className="email-detail-nadia-chat__input"
          placeholder="Posez votre question à Nadia..."
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
        />
        <button type="button" className="email-detail-nadia-chat__send" disabled={!chatInput.trim()}>
          <IconSend />
        </button>
      </div>
    </div>
  );
}
