const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const path = require("path");
const fs = require("fs");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  win.loadURL("http://localhost:3000");
}

app.whenReady().then(createWindow);

// =========================
// 📁 Selecionar pasta
// =========================
ipcMain.handle("select-folder", async () => {
  const result = await dialog.showOpenDialog({
    properties: ["openDirectory"]
  });

  if (result.canceled) return [];

  const folderPath = result.filePaths[0];

  const files = fs.readdirSync(folderPath);

  return files
    .filter(f =>
      f.toLowerCase().endsWith(".jpg") ||
      f.toLowerCase().endsWith(".png") ||
      f.toLowerCase().endsWith(".jpeg")
    )
    .map(f => ({
      path: path.join(folderPath, f),
      name: f
    }));
});

// =========================
// 📄 Ler imagem (base64)
// =========================
ipcMain.handle("read-file", async (_, filePath) => {
  const file = fs.readFileSync(filePath);

  const ext = path.extname(filePath).toLowerCase();

  const mime =
    ext === ".png" ? "image/png" :
    ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" :
    "application/octet-stream";

  return `data:${mime};base64,${file.toString("base64")}`;
});