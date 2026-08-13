import type { StarButtonProps } from "../../../models";
import { IconStar } from "../icons";
import { getStarTitle } from "../../../constants/labels";
import "./StarButton.css";

export default function StarButton({ starred, onToggle }: StarButtonProps) {
  return (
    <button
      type="button"
      className={`star-btn${starred ? " star-btn--active" : ""}`}
      title={getStarTitle(starred)}
      onClick={(e) => {
        e.stopPropagation();
        onToggle();
      }}
    >
      <IconStar filled={starred} />
    </button>
  );
}
