import type { ErrorMessageProps } from "../../types/ui/ErrorMessageProps";
import { colors, spacing, radius } from "../../styles";


export default function ErrorMessage({ message, style }: ErrorMessageProps) {
  return (
    <div
      role="alert"
      style={{
        padding: spacing.card,
        backgroundColor: colors.errorLight,
        color: colors.error,
        borderRadius: radius.sm,
        fontSize: "13px",
        ...style,
      }}
    >
      {message}
    </div>
  );
}
