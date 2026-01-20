import { spawn } from "node:child_process";
import path from "node:path";
import { app } from "electron";
import { platform } from "node:os";

export function launchBackend() {
  if (!app.isPackaged) {
    const backendDir = path.join(__dirname, "../../../backend");
    const projectRoot = path.join(__dirname, "../../..");
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
      }
    );

    backendProcess.on("error", (err) => {
      console.error("DEV backend failed:", err);
    });

  if (!fs.existsSync(backendPath)) {
    console.error("Backend introuvable:", backendPath);
    return;
  }

  if (process.platform !== "win32") {
    try {
      fs.chmodSync(backendPath, 0o755);
    } catch (e: Error | any) {
      console.warn("chmod backend failed:", e.message);
    }
  }

  const child = spawn(backendPath, [], {
    stdio: "inherit",
    cwd: path.dirname(backendPath),
    env: {
      ...process.env,
    },
  });

  child.on("error", (err: Error) => {
    console.error("Erreur lancement backend:", err);
  });

  child.on("exit", (code: number) => {
    console.log("Backend exited with code", code);
  });
}
export { launchBackend };
