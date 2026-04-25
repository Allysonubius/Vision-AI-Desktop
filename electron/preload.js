const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  
  // 📁 abrir pasta
  selectFolder: () => ipcRenderer.invoke("select-folder"),

  // 📄 ler imagem (retorna base64 pronto)
  readFile: (path) => ipcRenderer.invoke("read-file", path)

});