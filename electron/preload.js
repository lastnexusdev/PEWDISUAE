const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('api', {
  register: (payload) => ipcRenderer.invoke('auth:register', payload),
  login: (payload) => ipcRenderer.invoke('auth:login', payload),
  listProducts: () => ipcRenderer.invoke('products:list'),
  createProduct: (payload) => ipcRenderer.invoke('products:create', payload),
  listInventoryByUser: (userId) => ipcRenderer.invoke('inventory:listByUser', userId),
  createInventory: (payload) => ipcRenderer.invoke('inventory:create', payload)
});
