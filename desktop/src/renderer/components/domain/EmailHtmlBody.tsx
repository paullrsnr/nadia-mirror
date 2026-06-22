import { useCallback, useRef, useState } from "react";
import "./EmailHtmlBody.css";

interface EmailHtmlBodyProps {
  html: string;
}

const RICH_CONTENT_PATTERN = /<img[\s>]|<table[\s>]|background(-color|-image)?\s*[:=]/i;

export function isRichHtml(html: string): boolean {
  return RICH_CONTENT_PATTERN.test(html);
}

const BASE_STYLE = `
  <style>
    html, body { margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
      color: #1a1a1a;
      word-break: break-word;
      overflow-wrap: anywhere;
    }
    img { max-width: 100%; height: auto; }
    a { color: #3b6dd6; }
    table { max-width: 100%; }
  </style>
`;

export default function EmailHtmlBody({ html }: EmailHtmlBodyProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [height, setHeight] = useState(0);

  const handleLoad = useCallback(() => {
    const doc = iframeRef.current?.contentWindow?.document;
    if (doc?.documentElement) {
      setHeight(doc.documentElement.scrollHeight);
    }
  }, []);

  const srcDoc = `<!DOCTYPE html><html><head><base target="_blank">${BASE_STYLE}</head><body>${html}</body></html>`;

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
