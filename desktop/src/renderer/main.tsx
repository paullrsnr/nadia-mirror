import React from "react";
import ReactDOM from "react-dom/client";
import Inbox from "./pages/Inbox";

const root = ReactDOM.createRoot(
  document.getElementById("root") as HTMLElement
);

root.render(
  <React.StrictMode>
    <Inbox />
  </React.StrictMode>
);
