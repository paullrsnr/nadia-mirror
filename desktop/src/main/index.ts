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

async function logoutBeforeQuit(): Promise<void> {
  try {
    await fetch(`${API_BASE_URL}/auth/logout`, { method: "POST" });
  } catch (error) {
    // Ignorer les erreurs (le backend peut déjà être arrêté)
  }
}

app.whenReady().then(async () => {
  launchBackend();
  createWindow();
});

let isQuitting = false;

app.on("before-quit", async (event) => {
  if (isQuitting) return;
  
  event.preventDefault();
  isQuitting = true;
  await logoutBeforeQuit();
  app.exit();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});
