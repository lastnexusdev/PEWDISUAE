let currentUser = null;

const authSection = document.getElementById('authSection');
const appSection = document.getElementById('appSection');
const authError = document.getElementById('authError');

async function refreshProducts() {
  const products = await window.api.listProducts();
  const select = document.getElementById('invProduct');
  select.innerHTML = '<option value="">Select product</option>';
  products.forEach((p) => {
    const opt = document.createElement('option');
    opt.value = p.id;
    opt.innerText = `${p.name} (${p.sizeValue} ${p.sizeUnit})`;
    select.appendChild(opt);
  });
}

async function refreshInventory() {
  if (!currentUser) return;
  const rows = await window.api.listInventoryByUser(currentUser.id);
  const tbody = document.getElementById('inventoryRows');
  tbody.innerHTML = '';
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.product?.name || '-'}</td>
      <td>${row.purchasedAt || '-'}</td>
      <td>${row.openedAt || '-'}</td>
      <td>${row.cadenceValue || '-'} ${row.cadenceUnit || ''}</td>
      <td>${row.amountPerUse || '-'}</td>
      <td>${row.expectedRunOutAt || '-'}</td>
    `;
    tbody.appendChild(tr);
  });
}

function enterApp(user) {
  currentUser = user;
  authSection.classList.add('hidden');
  appSection.classList.remove('hidden');
  document.getElementById('who').innerText = `${user.displayName} (${user.email})`;
  refreshProducts();
  refreshInventory();
}

document.getElementById('registerBtn').addEventListener('click', async () => {
  try {
    authError.textContent = '';
    const user = await window.api.register({
      displayName: document.getElementById('regName').value,
      email: document.getElementById('regEmail').value,
      password: document.getElementById('regPassword').value
    });
    enterApp(user);
  } catch (err) {
    authError.textContent = err.message;
  }
});

document.getElementById('loginBtn').addEventListener('click', async () => {
  try {
    authError.textContent = '';
    const user = await window.api.login({
      email: document.getElementById('loginEmail').value,
      password: document.getElementById('loginPassword').value
    });
    enterApp(user);
  } catch (err) {
    authError.textContent = err.message;
  }
});

document.getElementById('addProductBtn').addEventListener('click', async () => {
  await window.api.createProduct({
    name: document.getElementById('pName').value,
    category: document.getElementById('pCategory').value,
    sizeValue: document.getElementById('pSize').value,
    sizeUnit: document.getElementById('pUnit').value
  });
  await refreshProducts();
});

document.getElementById('addInventoryBtn').addEventListener('click', async () => {
  if (!currentUser) return;
  await window.api.createInventory({
    userId: currentUser.id,
    productId: document.getElementById('invProduct').value,
    purchasedAt: document.getElementById('invPurchased').value,
    openedAt: document.getElementById('invOpened').value,
    cadenceValue: document.getElementById('invCadenceValue').value,
    cadenceUnit: document.getElementById('invCadenceUnit').value,
    amountPerUse: document.getElementById('invAmountPerUse').value
  });
  await refreshInventory();
});
