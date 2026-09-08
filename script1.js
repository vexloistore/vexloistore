// script.js

// --- GESTIÓN DEL CARRITO DE COMPRAS ---
function getCart() {
  const cart = localStorage.getItem('vexloi_cart');
  return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
  localStorage.setItem('vexloi_cart', JSON.stringify(cart));
  updateCartCounter();
  renderCartDrawer();
}

function addToCart(productId, qtyInputId = null, minQty = 1) {
  const product = productsData.find(p => p.id === productId);
  if (!product) return;

  let qty = minQty;
  if (qtyInputId) {
    const inputEl = document.getElementById(qtyInputId);
    if (inputEl) {
      qty = parseInt(inputEl.value) || minQty;
    }
  }

  const cart = getCart();
  const existingIndex = cart.findIndex(item => item.id === productId);

  if (existingIndex > -1) {
    cart[existingIndex].qty += qty;
  } else {
    cart.push({
      id: product.id,
      name: product.name,
      price: product.price,
      sku: product.sku,
      image: product.image,
      brand: product.brand,
      qty: qty,
      minQty: minQty
    });
  }

  saveCart(cart);
  openCartDrawer();
}

function updateCartItemQty(productId, delta) {
  let cart = getCart();
  const index = cart.findIndex(item => item.id === productId);
  
  if (index > -1) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) {
      cart.splice(index, 1);
    }
    saveCart(cart);
  }
}

function updateCartCounter() {
  const cart = getCart();
  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
  const counterEl = document.getElementById('cart-counter');
  if (counterEl) {
    counterEl.innerText = totalItems;
  }
}

function renderCartDrawer() {
  const drawerItems = document.getElementById('cart-drawer-items');
  const cartTotal = document.getElementById('cart-total');
  const cart = getCart();

  if (!drawerItems) return;

  if (cart.length === 0) {
    drawerItems.innerHTML = `
      <div class="text-center py-8 text-gray-400 text-xs">
        Your wholesale cart is empty.
      </div>
    `;
    if (cartTotal) cartTotal.innerText = '$0.00 USD';
    return;
  }

  let total = 0;
  drawerItems.innerHTML = cart.map(item => {
    const itemTotal = item.price * item.qty;
    total += itemTotal;
    return `
      <div class="flex items-center justify-between p-2 bg-gray-50 rounded border border-gray-200">
        <div class="flex-1 pr-2">
          <p class="text-xs font-bold text-gray-800 line-clamp-1">${item.name}</p>
          <p class="text-[10px] text-gray-500">$${item.price.toFixed(2)} USD c/u</p>
          <div class="flex items-center space-x-2 mt-1">
            <button onclick="updateCartItemQty('${item.id}', -1)" class="px-1.5 py-0.5 bg-gray-200 text-xs font-bold rounded hover:bg-red-500 hover:text-white">-</button>
            <span class="text-xs font-bold">${item.qty}</span>
            <button onclick="updateCartItemQty('${item.id}', 1)" class="px-1.5 py-0.5 bg-gray-200 text-xs font-bold rounded hover:bg-brand-red hover:text-white">+</button>
          </div>
        </div>
        <div class="text-right">
          <p class="text-xs font-black text-brand-dark">$${itemTotal.toFixed(2)}</p>
        </div>
      </div>
    `;
  }).join('');

  if (cartTotal) cartTotal.innerText = `$${total.toFixed(2)} USD`;
}

function openCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  if (drawer && overlay) {
    drawer.classList.remove('translate-x-full');
    overlay.classList.remove('hidden');
  }
}

function closeCartDrawer() {
  const drawer = document.getElementById('cart-drawer');
  const overlay = document.getElementById('cart-overlay');
  if (drawer && overlay) {
    drawer.classList.add('translate-x-full');
    overlay.classList.add('hidden');
  }
}

// --- RENDERIZADO DE PRODUCTOS Y CATALOGO ---
function createProductCardHTML(p) {
  return `
    <div class="bg-white rounded-xl border border-gray-200 p-4 shadow-sm hover:shadow-md transition flex flex-col justify-between group">
      <div>
        <div class="h-44 bg-gray-50 rounded-lg p-2 mb-3 flex items-center justify-center overflow-hidden border border-gray-100">
          <img src="${p.image}" alt="${p.name}" class="max-h-full object-contain group-hover:scale-105 transition duration-300" onerror="this.src='https://via.placeholder.com/200?text=${encodeURIComponent(p.brand)}'">
        </div>
        <span class="text-[10px] font-bold text-brand-red uppercase tracking-wider">${p.brand}</span>
        <h3 class="text-xs font-bold text-brand-dark uppercase line-clamp-2 mt-0.5 mb-1" title="${p.name}">
          <a href="product-detail.html?id=${p.id}">${p.name}</a>
        </h3>
        <p class="text-[10px] text-gray-400 font-mono mb-2">SKU: ${p.sku}</p>
      </div>

      <div>
        <div class="flex justify-between items-center mb-3">
          <span class="text-sm font-black text-brand-dark">$${p.price.toFixed(2)} <span class="text-[10px] text-gray-400 font-normal">USD</span></span>
          <span class="text-[10px] bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded font-bold">★ ${p.rating}</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <a href="product-detail.html?id=${p.id}" class="text-center border border-gray-300 text-gray-700 hover:border-gray-800 text-[11px] font-bold py-2 rounded uppercase tracking-wider transition">
            Details
          </a>
          <button onclick="addToCart('${p.id}')" class="bg-brand-red hover:bg-red-700 text-white text-[11px] font-bold py-2 rounded uppercase tracking-wider transition">
            + Add
          </button>
        </div>
      </div>
    </div>
  `;
}

function renderCatalog(brand = 'all', category = 'all', search = '') {
  const container = document.getElementById('catalog-products-grid');
  const countEl = document.getElementById('result-count');
  if (!container) return;

  let filtered = productsData;

  if (brand !== 'all') {
    filtered = filtered.filter(p => p.brand.toLowerCase().replace(/['\s]/g, '-') === brand.toLowerCase());
  }

  if (category !== 'all') {
    filtered = filtered.filter(p => p.category === category);
  }

  if (search.trim() !== '') {
    const term = search.toLowerCase();
    filtered = filtered.filter(p => 
      p.name.toLowerCase().includes(term) || 
      p.sku.toLowerCase().includes(term) || 
      p.brand.toLowerCase().includes(term)
    );
  }

  if (countEl) {
    countEl.innerText = `Showing ${filtered.length} of ${productsData.length} Products`;
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="col-span-full text-center py-12 bg-white rounded-xl border border-gray-200">
        <p class="text-sm font-bold text-gray-500">No products match your criteria.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(p => createProductCardHTML(p)).join('');
  if (window.lucide) lucide.createIcons();
}

// --- GESTIÓN DE USUARIOS B2B Y SESIÓN LOCAL ---
function getUsers() {
  const users = localStorage.getItem('vexloi_users');
  return users ? JSON.parse(users) : [];
}

function getActiveUser() {
  const active = localStorage.getItem('vexloi_active_user');
  return active ? JSON.parse(active) : null;
}

function registerUser(userData) {
  const users = getUsers();
  if (users.some(u => u.email === userData.email)) {
    return { success: false, message: 'El correo electrónico ya está registrado.' };
  }
  users.push(userData);
  localStorage.setItem('vexloi_users', JSON.stringify(users));
  localStorage.setItem('vexloi_active_user', JSON.stringify(userData));
  return { success: true };
}

function loginUser(email, password) {
  const users = getUsers();
  const user = users.find(u => u.email === email && u.password === password);
  if (user) {
    localStorage.setItem('vexloi_active_user', JSON.stringify(user));
    return { success: true };
  }
  return { success: false, message: 'Credenciales inválidas. Verifica tu correo y contraseña.' };
}

function logoutUser() {
  localStorage.removeItem('vexloi_active_user');
  window.location.reload();
}

function updateHeaderUserNav() {
  const navContainer = document.getElementById('user-header-nav');
  if (!navContainer) return;

  const activeUser = getActiveUser();
  if (activeUser) {
    navContainer.innerHTML = `
      <div class="flex items-center space-x-2 text-xs">
        <span class="font-bold text-gray-700 hidden sm:inline">${activeUser.company || activeUser.name}</span>
        <button onclick="logoutUser()" class="text-brand-red font-bold hover:underline uppercase text-[10px]">Logout</button>
      </div>
    `;
  } else {
    navContainer.innerHTML = `
      <a href="login.html" class="text-xs font-bold text-brand-dark hover:text-brand-red uppercase flex items-center gap-1">
        <i data-lucide="user" class="w-4 h-4"></i> Account
      </a>
    `;
  }
}

// --- INICIALIZACIÓN GLOBAL ---
document.addEventListener('DOMContentLoaded', () => {
  updateCartCounter();
  renderCartDrawer();
  updateHeaderUserNav();
});