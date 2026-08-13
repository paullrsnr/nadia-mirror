import { useCallback, useMemo, useRef, useState } from "react";
import "./EmailHtmlBody.css";
import { useTheme } from "../../../hooks/useTheme";
import type { ResolvedTheme } from "../../../models/theme";
import type { EmailHtmlBodyProps } from "../../../models/email";

const RICH_CONTENT_PATTERN = /<img[\s>]|<table[\s>]|background(-color|-image)?\s*[:=]/i;

export function isRichHtml(html: string): boolean {
  return RICH_CONTENT_PATTERN.test(html);
}

const resolvedColorCache = new Map<string, string>();

function resolveThemeColor(cssVar: string, theme: ResolvedTheme): string {
  const cacheKey = `${theme}:${cssVar}`;
  const cached = resolvedColorCache.get(cacheKey);
  if (cached) return cached;

  const probe = document.createElement("div");
  probe.style.display = "none";
  probe.setAttribute("data-theme", theme);
  document.body.appendChild(probe);
  const value = getComputedStyle(probe).getPropertyValue(cssVar).trim();
  document.body.removeChild(probe);

  resolvedColorCache.set(cacheKey, value);
  return value;
}

function buildBaseStyle(theme: ResolvedTheme): string {
  const textColor = resolveThemeColor("--color-content", theme);
  const linkColor = resolveThemeColor("--color-marque-primary", theme);
  return `
  <style>
    html, body { margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      color: ${textColor};
      word-break: break-word;
      overflow-wrap: anywhere;
    }
    img { max-width: 100%; height: auto; }
    a { color: ${linkColor}; }
    table { max-width: 100%; }
  </style>
`;
}

export default function EmailHtmlBody({ html }: EmailHtmlBodyProps) {
  const { theme } = useTheme();
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(0);

  const handleLoad = useCallback(() => {
    const doc = iframeRef.current?.contentWindow?.document;
    if (doc?.documentElement) {
      setHeight(doc.documentElement.scrollHeight);
    }
  }, []);

  const srcDoc = useMemo(
    () =>
      `<!DOCTYPE html><html><head><base target="_blank">${buildBaseStyle(theme)}</head><body>${html}</body></html>`,
    [html, theme],
  );

  return (
    <iframe
      ref={iframeRef}
      className="email-html-body"
      style={{ height }}
      srcDoc={srcDoc}
      sandbox="allow-same-origin allow-popups"
      onLoad={handleLoad}
      title="Contenu de l'email"
    />
  );
}
