import { spawn } from "child_process";
import path from "path";
import { app } from "electron";

export function launchBackend() {
  if (!app.isPackaged) {
    const backendDir = path.join(__dirname, "../../../backend");
    const pythonPath = path.join(backendDir, ".venv", "bin", "python3");

    const backendProcess = spawn(
      pythonPath,
      ["-m", "uvicorn", "api.main:app", "--reload", "--port", "3333"],
      {
        cwd: backendDir,
        stdio: "inherit",
      }
    );

    backendProcess.on("error", (err) => {
      console.error("DEV backend failed:", err);
    });

    return;
  }

  const backendBinaryPath = path.join(
    process.resourcesPath,
    "backend",
    "nadia-backend"
  );

  const backendProcess = spawn(backendBinaryPath, [], {
    stdio: "inherit",
  });

  backendProcess.on("error", (err) => {
    console.error("PROD backend failed:", err);
  });
}
