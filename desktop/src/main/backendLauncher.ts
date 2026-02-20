import { spawn } from "node:child_process";
import path from "node:path";
import fs from "node:fs";
import { app } from "electron";
import { platform } from "node:os";

export function launchBackend() {
  if (!app.isPackaged) {
    // Mode développement
    const backendDir = path.join(__dirname, "../../../backend");
    const projectRoot = path.join(__dirname, "../../..");
    // Le modèle GGUF est stocké côté backend (backend/ressources)
    const resourcesPath = path.join(projectRoot, "backend", "ressources");
    const isWindows = platform() === "win32";
    const pythonPath = isWindows
      ? path.join(backendDir, ".venv", "Scripts", "python.exe")
      : path.join(backendDir, ".venv", "bin", "python3");

    // Lancer depuis le répertoire parent pour que les imports backend.* fonctionnent
    const backendProcess = spawn(
      pythonPath,
      ["-m", "uvicorn", "backend.api.main:app", "--reload", "--port", "3333"],
      {
        cwd: projectRoot,
        stdio: "inherit",
        env: {
          ...process.env,
          RESOURCES_PATH: resourcesPath,
        },
      }
    );

    backendProcess.on("error", (err) => {
      console.error("DEV backend failed:", err);
    });

    return;
  }

  // Mode production
  const isWindows = platform() === "win32";
  const backendBinaryName = isWindows ? "nadia-backend.exe" : "nadia-backend";
  const resourcesPath = process.resourcesPath || app.getAppPath();
  const llmResourcesPath = path.join(resourcesPath, "backend", "ressources");
  const backendPath = path.join(
    resourcesPath,
    "backend",
    backendBinaryName
  );

  if (!fs.existsSync(backendPath)) {
    console.error("Backend introuvable:", backendPath);
    return;
  }

  if (process.platform !== "win32") {
    try {
      fs.chmodSync(backendPath, 0o755);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Unknown error");
      console.warn("chmod backend failed:", error.message);
    }
  }

  const child = spawn(backendPath, [], {
    stdio: "ignore",
    windowsHide: true,
    detached: false,
    cwd: path.dirname(backendPath),
    env: {
      ...process.env,
      RESOURCES_PATH: llmResourcesPath,
    },
  });

  child.on("error", (err: Error) => {
    console.error("Erreur lancement backend:", err);
  });

  child.on("exit", (code: number) => {
    console.log("Backend exited with code", code);
  });
}
