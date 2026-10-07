// script.js — Vexloi LLC Tech Wholesale

const CART_KEY = 'vexloi_tech_cart';
const USERS_KEY = 'vexloi_tech_users';
const ACTIVE_USER_KEY = 'vexloi_tech_active_user';

// --- UTILIDADES ---
function esc(str) {
  return String(str ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function money(n) {
  return '$' + Number(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function getCategory(id) {
  return categoriesDict[id] || categoriesDict[String(id)];
}

function getCategoryIdBySlug(slug) {
  return Number(Object.keys(categoriesDict).find(id => categoriesDict[id].slug === slug)) || null;
}

function countBy(list, fn) {
  return list.reduce((acc, item) => { const k = fn(item); acc[k] = (acc[k] || 0) + 1; return acc; }, {});
}

function storageGet(key, fallback) {
  try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch (e) { return fallback; }
}

function storageSet(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch (e) { /* almacenamiento no disponible */ }
}

function starsHTML(rating) {
  const full = Math.round(rating || 0);
  return `<span class="text-amber-400 text-xs tracking-tight">${'★'.repeat(full)}<span class="text-gray-300">${'★'.repeat(5 - full)}</span></span>`;
}

function imgFallback(brand) {
  return `https://placehold.co/400x400/F1F5F9/64748B?text=${encodeURIComponent(brand)}`;
}

// --- LAYOUT COMPARTIDO (header, footer, carrito) ---
const NAV_LINKS = [
  { page: 'home', href: 'index.html', label: 'Home' },
  { page: 'catalog', href: 'catalog.html', label: 'Catalog' },
  { page: 'brands', href: 'brands.html', label: 'Brands' },
  { page: 'about', href: 'about.html', label: 'About Us' },
  { page: 'contact', href: 'contact.html', label: 'Contact' },
];

function renderHeader() {
  const el = document.getElementById('site-header');
  if (!el) return;
  const active = document.body.dataset.page;
  const cats = Object.entries(categoriesDict);

  el.innerHTML = `
    <div class="bg-brand-ink text-gray-300 text-2xs">
      <div class="container-custom py-2 flex items-center justify-between gap-4">
        <span class="flex items-center gap-2"><i data-lucide="cpu" class="w-3.5 h-3.5 text-brand-cyan"></i> B2B Wholesale Electronics & Technology | Direct Export from Miami, FL</span>
        <span class="hidden md:flex items-center gap-5">
          <span class="flex items-center gap-1"><i data-lucide="shield-check" class="w-3.5 h-3.5"></i> 100% Factory Sealed</span>
          <span class="flex items-center gap-1"><i data-lucide="truck" class="w-3.5 h-3.5"></i> Freight Forwarder Ready</span>
          <a href="contact.html" class="hover:text-white">sales@vexloi.com</a>
        </span>
      </div>
    </div>

    <header class="bg-brand-navy text-white sticky top-0 z-40 shadow-lg">
      <div class="container-custom py-3 flex items-center gap-4 md:gap-8">
        <a href="index.html" class="flex items-center gap-2 shrink-0">
          <span class="w-9 h-9 rounded-lg bg-brand-blue flex items-center justify-center"><i data-lucide="zap" class="w-5 h-5"></i></span>
          <span class="text-xl font-extrabold tracking-tight">VEXLOI <span class="text-brand-cyan">LLC</span></span>
        </a>

        <form action="catalog.html" class="hidden md:flex flex-1 max-w-2xl">
          <div class="flex w-full bg-white rounded-lg overflow-hidden">
            <input name="q" type="search" placeholder="Search 3,000+ products, brands, ASIN or UPC..." class="flex-1 px-4 py-2.5 text-sm text-gray-800 focus:outline-none">
            <button class="bg-brand-blue hover-bg-brand-blue-dark px-5 flex items-center" aria-label="Search"><i data-lucide="search" class="w-4 h-4"></i></button>
          </div>
        </form>

        <div class="flex items-center gap-4 ml-auto">
          <div id="user-header-nav"></div>
          <button onclick="openCartDrawer()" class="relative flex items-center gap-2 hover:text-blue-300 transition" aria-label="Open cart">
            <i data-lucide="shopping-cart" class="w-6 h-6"></i>
            <span id="cart-counter" class="absolute -top-2 -right-2 bg-brand-cyan text-brand-ink text-3xs font-bold rounded-full h-5 min-w-5 px-1 flex items-center justify-center" style="min-width:1.25rem">0</span>
          </button>
          <button onclick="toggleMobileMenu()" class="md:hidden" aria-label="Menu">
            <i data-lucide="menu" id="menu-icon-open" class="w-7 h-7"></i>
            <i data-lucide="x" id="menu-icon-close" class="w-7 h-7 hidden"></i>
          </button>
        </div>
      </div>

      <nav class="hidden md:block border-t border-white border-opacity-10 bg-brand-panel">
        <div class="container-custom flex items-center gap-6 text-sm">
          <div class="mega-wrap relative">
            <button class="flex items-center gap-2 bg-brand-blue px-4 py-2.5 font-semibold text-sm">
              <i data-lucide="layout-grid" class="w-4 h-4"></i> All Categories <i data-lucide="chevron-down" class="w-4 h-4"></i>
            </button>
            <div class="mega absolute left-0 top-full w-screen max-w-4xl bg-white text-gray-800 rounded-b-xl shadow-2xl p-5 z-50">
              <div class="grid grid-cols-3 gap-1">
                ${cats.map(([id, c]) => `
                  <a href="catalog.html?cat=${c.slug}" class="flex items-center gap-3 p-2 rounded-lg hover:bg-blue-50 group">
                    <span class="w-8 h-8 rounded-md bg-blue-50 text-brand-blue flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white"><i data-lucide="${c.icon}" class="w-4 h-4"></i></span>
                    <span class="text-xs font-semibold">${esc(c.name)}</span>
                  </a>`).join('')}
              </div>
            </div>
          </div>
          ${NAV_LINKS.map(l => `<a href="${l.href}" class="py-2.5 font-medium ${active === l.page ? 'text-brand-cyan' : 'text-gray-300 hover:text-white'}">${l.label}</a>`).join('')}
          <a href="checkout.html" class="py-2.5 font-medium ml-auto ${active === 'checkout' ? 'text-brand-cyan' : 'text-gray-300 hover:text-white'} flex items-center gap-1"><i data-lucide="file-text" class="w-4 h-4"></i> Checkout / Proforma</a>
        </div>
      </nav>

      <div id="mobile-menu" class="hidden md:hidden bg-brand-panel border-t border-white border-opacity-10 px-4 py-4 space-y-3">
        <form action="catalog.html" class="flex bg-white rounded-lg overflow-hidden">
          <input name="q" type="search" placeholder="Search products..." class="flex-1 px-3 py-2 text-sm text-gray-800 focus:outline-none">
          <button class="bg-brand-blue px-4" aria-label="Search"><i data-lucide="search" class="w-4 h-4"></i></button>
        </form>
        ${NAV_LINKS.concat([{ page: 'checkout', href: 'checkout.html', label: 'Checkout' }]).map(l => `<a href="${l.href}" class="block text-sm font-semibold ${active === l.page ? 'text-brand-cyan' : 'text-gray-200'}">${l.label}</a>`).join('')}
        <details class="text-sm text-gray-200">
          <summary class="font-semibold cursor-pointer">Categories</summary>
          <div class="mt-2 space-y-2 pl-2">
            ${cats.map(([, c]) => `<a href="catalog.html?cat=${c.slug}" class="block text-xs text-gray-300">${esc(c.name)}</a>`).join('')}
          </div>
        </details>
      </div>
    </header>
  `;
}

function renderFooter() {
  const el = document.getElementById('site-footer');
  if (!el) return;
  const cats = Object.values(categoriesDict);
  el.innerHTML = `
    <footer class="bg-brand-ink text-gray-400 text-xs mt-auto">
      <div class="container-custom py-12 grid grid-cols-2 md:grid-cols-5 gap-8">
        <div class="col-span-2">
          <div class="flex items-center gap-2 mb-3">
            <span class="w-8 h-8 rounded-lg bg-brand-blue flex items-center justify-center text-white"><i data-lucide="zap" class="w-4 h-4"></i></span>
            <span class="text-lg font-extrabold text-white">VEXLOI <span class="text-brand-cyan">LLC</span></span>
          </div>
          <p class="leading-relaxed max-w-sm">Import, export and wholesale distribution of consumer electronics, pro audio/video, networking, security and industrial technology. Doral / Miami, FL.</p>
          <p class="mt-3 text-gray-500">sales@vexloi.com</p>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-3 text-sm">Top Categories</h4>
          <ul class="space-y-2">${cats.slice(0, 7).map(c => `<li><a class="hover:text-white" href="catalog.html?cat=${c.slug}">${esc(c.name)}</a></li>`).join('')}</ul>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-3 text-sm">Company</h4>
          <ul class="space-y-2">
            <li><a class="hover:text-white" href="about.html">About Us</a></li>
            <li><a class="hover:text-white" href="brands.html">All Brands</a></li>
            <li><a class="hover:text-white" href="contact.html">Wholesale Inquiries</a></li>
            <li><a class="hover:text-white" href="login.html">B2B Account</a></li>
          </ul>
        </div>
        <div>
          <h4 class="text-white font-semibold mb-3 text-sm">Policies</h4>
          <ul class="space-y-2">
            <li><a class="hover:text-white" href="privacy-policy.html">Privacy Policy</a></li>
            <li><a class="hover:text-white" href="accessibility-policy.html">Accessibility Policy</a></li>
            <li><a class="hover:text-white" href="terms-and-conditions.html">Terms & Conditions</a></li>
            <li><a class="hover:text-white" href="returns-policy.html">Returns & Warranty</a></li>
          </ul>
        </div>
      </div>
      <div class="border-t border-white border-opacity-10">
        <div class="container-custom py-5 flex flex-col md:flex-row justify-between gap-2 text-gray-500">
          <span>&copy; 2026 Vexloi LLC. All rights reserved.</span>
          <span>All trademarks belong to their respective owners. Prices shown are reference prices in USD.</span>
        </div>
      </div>
    </footer>

    <div id="cart-overlay" onclick="closeCartDrawer()" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden"></div>
    <aside id="cart-drawer" class="fixed top-0 right-0 w-full sm:w-96 h-full bg-white z-50 shadow-2xl flex flex-col transform translate-x-full transition-transform duration-300">
      <div class="p-4 flex items-center justify-between bg-brand-navy text-white">
        <h3 class="font-semibold text-sm flex items-center gap-2"><i data-lucide="shopping-cart" class="w-4 h-4"></i> Your Wholesale Cart</h3>
        <button onclick="closeCartDrawer()" class="text-gray-400 hover:text-white" aria-label="Close cart"><i data-lucide="x" class="w-5 h-5"></i></button>
      </div>
      <div id="cart-drawer-items" class="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-thin"></div>
      <div class="p-4 border-t border-gray-200 bg-gray-50 space-y-3">
        <div class="flex justify-between items-center text-sm font-semibold">
          <span>Subtotal</span>
          <span id="cart-total" class="text-lg font-extrabold text-brand-ink">$0.00</span>
        </div>
        <a href="checkout.html" class="btn-primary w-full">Proceed to B2B Checkout <i data-lucide="arrow-right" class="w-4 h-4"></i></a>
      </div>
    </aside>
  `;
}

// --- CARRITO ---
function getCart() { return storageGet(CART_KEY, []); }

function saveCart(cart) {
  storageSet(CART_KEY, cart);
  updateCartCounter();
  renderCartDrawer();
}

function addToCart(productId, qtyInputId = null, minQty = 1) {
  const product = productsData.find(p => p.id === productId);
  if (!product) return;

  let qty = minQty;
  if (qtyInputId) {
    const inputEl = document.getElementById(qtyInputId);
    if (inputEl) qty = Math.max(minQty, parseInt(inputEl.value) || minQty);
  }

  const cart = getCart();
  const existing = cart.find(item => item.id === productId);
  if (existing) {
    existing.qty += qty;
  } else {
    cart.push({ id: product.id, name: product.name, price: product.price, sku: product.sku, image: product.image, brand: product.brand, qty, minQty });
  }
  saveCart(cart);
  openCartDrawer();
}

function updateCartItemQty(productId, delta) {
  const cart = getCart();
  const index = cart.findIndex(item => item.id === productId);
  if (index > -1) {
    cart[index].qty += delta;
    if (cart[index].qty <= 0) cart.splice(index, 1);
    saveCart(cart);
  }
}

function removeFromCart(productId) {
  saveCart(getCart().filter(item => item.id !== productId));
}

function clearCart() {
  try { localStorage.removeItem(CART_KEY); } catch (e) { /* noop */ }
  updateCartCounter();
  renderCartDrawer();
}

function updateCartCounter() {
  const el = document.getElementById('cart-counter');
  if (el) el.innerText = getCart().reduce((sum, item) => sum + item.qty, 0);
}

function renderCartDrawer() {
  const drawerItems = document.getElementById('cart-drawer-items');
  const cartTotal = document.getElementById('cart-total');
  if (!drawerItems) return;
  const cart = getCart();

  if (cart.length === 0) {
    drawerItems.innerHTML = `
      <div class="text-center py-12 text-gray-400 text-xs">
        <i data-lucide="package-open" class="w-10 h-10 mx-auto mb-3 text-gray-300"></i>
        Your wholesale cart is empty.
        <a href="catalog.html" class="block mt-3 text-brand-blue font-semibold">Browse the catalog &rarr;</a>
      </div>`;
    if (cartTotal) cartTotal.innerText = '$0.00 USD';
    if (window.lucide) lucide.createIcons();
    return;
  }

  let total = 0;
  drawerItems.innerHTML = cart.map(item => {
    const itemTotal = item.price * item.qty;
    total += itemTotal;
    return `
      <div class="flex gap-3 p-2.5 rounded-lg border border-gray-200">
        <img src="${esc(item.image)}" alt="" class="w-14 h-14 object-contain bg-white rounded" onerror="this.src='${imgFallback(item.brand)}'">
        <div class="flex-1 min-w-0">
          <p class="text-3xs font-bold text-brand-blue uppercase">${esc(item.brand)}</p>
          <p class="text-xs font-semibold text-gray-800 line-clamp-2">${esc(item.name)}</p>
          <div class="flex items-center justify-between mt-1.5">
            <div class="flex items-center border border-gray-300 rounded">
              <button onclick="updateCartItemQty('${item.id}', -1)" class="px-2 text-xs font-bold hover:text-brand-blue">−</button>
              <span class="text-xs font-bold px-1">${item.qty}</span>
              <button onclick="updateCartItemQty('${item.id}', 1)" class="px-2 text-xs font-bold hover:text-brand-blue">+</button>
            </div>
            <span class="text-xs font-extrabold text-brand-ink">${money(itemTotal)}</span>
          </div>
        </div>
        <button onclick="removeFromCart('${item.id}')" class="text-gray-400 hover:text-red-600 self-start" title="Remove item"><i data-lucide="trash-2" class="w-4 h-4"></i></button>
      </div>`;
  }).join('');

  if (cartTotal) cartTotal.innerText = `${money(total)} USD`;
  if (window.lucide) lucide.createIcons();
}

function openCartDrawer() {
  document.getElementById('cart-drawer')?.classList.remove('translate-x-full');
  document.getElementById('cart-overlay')?.classList.remove('hidden');
}

function closeCartDrawer() {
  document.getElementById('cart-drawer')?.classList.add('translate-x-full');
  document.getElementById('cart-overlay')?.classList.add('hidden');
}

// --- TARJETA DE PRODUCTO ---
function createProductCardHTML(p) {
  const cat = getCategory(p.categoryId);
  return `
    <div class="card card-hover p-3.5 flex flex-col">
      <a href="product-detail.html?id=${p.id}" class="block relative">
        <div class="product-img p-2">
          <img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy" onerror="this.src='${imgFallback(p.brand)}'">
        </div>
        ${p.rank <= 3 ? `<span class="badge badge-dark absolute top-1 left-1"><i data-lucide="flame" class="w-3 h-3"></i> #${p.rank} ${esc(p.brand)}</span>` : ''}
      </a>
      <div class="mt-3 flex-1 flex flex-col">
        <a href="catalog.html?brand=${p.brandId}" class="text-3xs font-bold text-brand-blue uppercase tracking-wider hover:underline">${esc(p.brand)}</a>
        <h3 class="text-xs font-semibold text-brand-ink line-clamp-2 mt-1 leading-snug" title="${esc(p.desc)}">
          <a href="product-detail.html?id=${p.id}" class="hover-text-brand-blue">${esc(p.name)}</a>
        </h3>
        <p class="text-3xs text-gray-400 mt-1 line-clamp-1">${esc(p.subcategory || (cat ? cat.name : ''))}</p>
        <div class="flex items-center gap-1 mt-1.5">${starsHTML(p.rating)}<span class="text-3xs text-gray-400">${p.rating ? p.rating.toFixed(1) : '—'} (${p.reviews.toLocaleString('en-US')})</span></div>
        <div class="mt-auto pt-3 flex items-end justify-between gap-2">
          <div>
            <div class="text-base font-extrabold text-brand-ink leading-none">${money(p.price)}</div>
            <div class="text-3xs text-gray-400 mt-0.5 font-mono">${p.sku}</div>
          </div>
          <button onclick="addToCart('${p.id}')" class="w-9 h-9 rounded-lg bg-brand-blue hover-bg-brand-blue-dark text-white flex items-center justify-center shrink-0" title="Add to cart" aria-label="Add to cart">
            <i data-lucide="plus" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    </div>`;
}

// --- USUARIOS B2B (sesión local de demostración) ---
function getUsers() { return storageGet(USERS_KEY, []); }
function getActiveUser() { return storageGet(ACTIVE_USER_KEY, null); }

function registerUser(userData) {
  const users = getUsers();
  if (users.some(u => u.email === userData.email)) {
    return { success: false, message: 'This email is already registered.' };
  }
  users.push(userData);
  storageSet(USERS_KEY, users);
  storageSet(ACTIVE_USER_KEY, userData);
  return { success: true };
}

function loginUser(email, password) {
  const user = getUsers().find(u => u.email === email && u.password === password);
  if (user) {
    storageSet(ACTIVE_USER_KEY, user);
    return { success: true };
  }
  return { success: false, message: 'Invalid credentials. Please check your email and password.' };
}

function logoutUser() {
  try { localStorage.removeItem(ACTIVE_USER_KEY); } catch (e) { /* noop */ }
  window.location.reload();
}

function updateHeaderUserNav() {
  const nav = document.getElementById('user-header-nav');
  if (!nav) return;
  const user = getActiveUser();
  nav.innerHTML = user
    ? `<div class="flex items-center gap-2 text-xs">
         <i data-lucide="building-2" class="w-4 h-4 text-brand-cyan"></i>
         <span class="font-semibold hidden sm:inline">${esc(user.company || user.name)}</span>
         <button onclick="logoutUser()" class="text-gray-400 hover:text-white underline text-3xs uppercase">Logout</button>
       </div>`
    : `<a href="login.html" class="flex items-center gap-1.5 text-xs font-semibold hover:text-blue-300">
         <i data-lucide="user" class="w-5 h-5"></i><span class="hidden sm:inline">Account</span>
       </a>`;
}

// --- MENÚ MÓVIL ---
function toggleMobileMenu() {
  document.getElementById('mobile-menu')?.classList.toggle('hidden');
  document.getElementById('menu-icon-open')?.classList.toggle('hidden');
  document.getElementById('menu-icon-close')?.classList.toggle('hidden');
}

// --- INICIALIZACIÓN GLOBAL ---
renderHeader();
renderFooter();
document.addEventListener('DOMContentLoaded', () => {
  updateCartCounter();
  renderCartDrawer();
  updateHeaderUserNav();
  if (window.lucide) lucide.createIcons();
});
