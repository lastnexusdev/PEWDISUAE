const path = require('path');
const crypto = require('crypto');
const { app, BrowserWindow, ipcMain } = require('electron');

const { Store } = require('./store');

const dataPath = path.join(app.getPath('userData'), 'corejunkie-data.json');
const store = new Store(dataPath);

function hashPassword(password, salt = crypto.randomBytes(16).toString('hex')) {
  const hash = crypto.pbkdf2Sync(password, salt, 200000, 32, 'sha256').toString('hex');
  return `${salt}:${hash}`;
}

function verifyPassword(password, stored) {
  const [salt, expected] = stored.split(':');
  const hash = crypto.pbkdf2Sync(password, salt, 200000, 32, 'sha256').toString('hex');
  return crypto.timingSafeEqual(Buffer.from(hash), Buffer.from(expected));
}

function cadenceToUsesPerDay(value, unit) {
  if (unit === 'day') return value;
  if (unit === 'week') return value / 7;
  throw new Error('cadence unit must be day/week');
}

function estimateRunoutDate(sizeValue, openedAt, cadenceValue, cadenceUnit, amountPerUse) {
  const usesPerDay = cadenceToUsesPerDay(Number(cadenceValue), cadenceUnit);
  const dailyUse = usesPerDay * Number(amountPerUse);
  if (!dailyUse) return null;
  const days = Math.round(Number(sizeValue) / dailyUse);
  const dt = new Date(openedAt);
  dt.setDate(dt.getDate() + days);
  return dt.toISOString().slice(0, 10);
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 820,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadFile(path.join(__dirname, 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  createWindow();
  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('auth:register', (_, payload) => {
  const { email, displayName, password } = payload;
  if (store.data.users.find(u => u.email === email)) {
    throw new Error('Email already exists');
  }
  const user = { id: store.nextId('user'), email, displayName, passwordHash: hashPassword(password) };
  store.data.users.push(user);
  store.save();
  return { id: user.id, email: user.email, displayName: user.displayName };
});

ipcMain.handle('auth:login', (_, payload) => {
  const user = store.data.users.find(u => u.email === payload.email);
  if (!user || !verifyPassword(payload.password, user.passwordHash)) {
    throw new Error('Invalid credentials');
  }
  return { id: user.id, email: user.email, displayName: user.displayName };
});

ipcMain.handle('products:list', () => {
  return store.data.products.sort((a, b) => a.name.localeCompare(b.name));
});

ipcMain.handle('products:create', (_, payload) => {
  const product = {
    id: store.nextId('product'),
    name: payload.name,
    category: payload.category,
    sizeValue: Number(payload.sizeValue),
    sizeUnit: payload.sizeUnit || 'fl_oz'
  };
  store.data.products.push(product);
  store.save();
  return product;
});

ipcMain.handle('inventory:listByUser', (_, userId) => {
  return store.data.inventory
    .filter(item => item.userId === userId)
    .map(item => ({ ...item, product: store.data.products.find(p => p.id === item.productId) || null }))
    .sort((a, b) => (a.createdAt < b.createdAt ? 1 : -1));
});

ipcMain.handle('inventory:create', (_, payload) => {
  const product = store.data.products.find(p => p.id === Number(payload.productId));
  if (!product) throw new Error('Product not found');

  let expectedRunOutAt = null;
  if (payload.openedAt && payload.cadenceValue && payload.cadenceUnit && payload.amountPerUse) {
    expectedRunOutAt = estimateRunoutDate(
      product.sizeValue,
      payload.openedAt,
      payload.cadenceValue,
      payload.cadenceUnit,
      payload.amountPerUse
    );
  }

  const row = {
    id: store.nextId('inventory'),
    userId: payload.userId,
    productId: Number(payload.productId),
    purchasedAt: payload.purchasedAt,
    openedAt: payload.openedAt || null,
    cadenceValue: payload.cadenceValue ? Number(payload.cadenceValue) : null,
    cadenceUnit: payload.cadenceUnit || null,
    amountPerUse: payload.amountPerUse ? Number(payload.amountPerUse) : null,
    expectedRunOutAt,
    createdAt: new Date().toISOString()
  };
  store.data.inventory.push(row);
  store.save();
  return row;
});
