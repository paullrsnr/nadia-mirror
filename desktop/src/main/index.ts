import { app, BrowserWindow } from "electron";
import path from "path";
import { launchBackend } from "./backendLauncher";

const API_BASE_URL = "http://127.0.0.1:3333"; // Dupliqué ici car main process séparé

let mainWindow: BrowserWindow | null = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
    },
  });

  const isDev = !app.isPackaged;

  if (isDev) {
    mainWindow.loadURL("http://localhost:5173");
  } else {
    mainWindow.loadFile(path.join(__dirname, "..", "renderer", "index.html"));
  }
}

app.whenReady().then(async () => {
  launchBackend();
  createWindow();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
