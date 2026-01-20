import { spawn } from "child_process";
import * as path from "path";
import fs from "fs";

function launchBackend() {
  const bin =
    process.platform === "win32" ? "nadia-backend.exe" : "nadia-backend";

  const backendPath = path.join(process.resourcesPath, "backend", bin);

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
