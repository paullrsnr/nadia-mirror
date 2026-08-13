const GREETING_PATTERN = /^(bonjour|cher|chère|madame|monsieur|salut|hello|hi)\b/i;
const SIGNOFF_PATTERN = /^(cordialement|bien à vous|bonne journée|bonne soirée|merci|à bientôt|sincèrement|amicalement)\b/i;
const SIGNATURE_NAME_PATTERN = /^[A-ZÀ-Ý][\wà-ÿ'-]*(\s+[A-ZÀ-Ý][\wà-ÿ'-]*){0,2}$/;
const SENTENCE_BOUNDARY = /(?<=[.!?])\s/;
const MAX_HEADLINE_LENGTH = 100;

export function extractReplyHeadline(text: string): string {
  const lines = text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const coreLine =
    lines.find(
      (line) =>
        !GREETING_PATTERN.test(line) &&
        !SIGNOFF_PATTERN.test(line) &&
        !SIGNATURE_NAME_PATTERN.test(line),
    ) ?? lines[0] ?? text;

  const firstSentence = coreLine.split(SENTENCE_BOUNDARY)[0].trim();
  return firstSentence.length > MAX_HEADLINE_LENGTH
    ? `${firstSentence.slice(0, MAX_HEADLINE_LENGTH - 3)}…`
    : firstSentence;
}
