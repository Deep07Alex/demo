class CartManager {
    constructor() {
        this.cartCountEl = document.getElementById('cartCount');
        this.cartSidebar = document.getElementById('cartSidebar');
        this.cartOverlay = document.getElementById('cartOverlay');
        this.init();
    }
    
    init() {
        this.attachEventListeners();
        this.updateCartDisplay();
    }
    
    attachEventListeners() {
        // Cart icon
        document.getElementById('cartIcon')?.addEventListener('click', () => this.openCart());
        document.getElementById('closeCartBtn')?.addEventListener('click', () => this.closeCart());
        this.cartOverlay?.addEventListener('click', () => this.closeCart());
        
        // Add to cart buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('add-to-cart-btn')) {
                e.preventDefault();
                const btn = e.target;
                this.addToCart({
                    id: btn.dataset.id,
                    type: btn.dataset.type,
                    title: btn.dataset.title,
                    price: btn.dataset.price,
                    image: btn.dataset.image
                });
            }
        });
    }
    
    async addToCart(product) {
        try {
            const response = await fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(product)
            });
            const data = await response.json();
            
            if (data.success) {
                this.updateCartDisplay();
                this.showNotification('Added to cart!');
                this.openCart();
            }
        } catch (error) {
            console.error('Cart error:', error);
        }
    }
    
    async removeFromCart(key) {
        await fetch('/cart/remove/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': this.getCSRFToken()},
            body: JSON.stringify({ key })
        });
        this.updateCartDisplay();
    }
    
    async updateQuantity(key, quantity) {
        await fetch('/cart/update/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': this.getCSRFToken()},
            body: JSON.stringify({ key, quantity })
        });
        this.updateCartDisplay();
    }
    
    async updateCartDisplay() {
        try {
            const response = await fetch('/cart/items/');
            const data = await response.json();
            
            if (this.cartCountEl) {
                if (data.cart_count > 0) {
                    this.cartCountEl.textContent = data.cart_count;
                    this.cartCountEl.style.display = 'flex';
                } else {
                    this.cartCountEl.style.display = 'none';
                }
            }
            
            this.renderCartItems(data.items || [], data.total || 0);
        } catch (error) {
            console.error('Display error:', error);
        }
    }
    
    renderCartItems(items, total) {
        const container = document.getElementById('cartItems');
        const footer = document.getElementById('cartFooter');
        
        if (!container) return;
        
        if (items.length === 0) {
            container.innerHTML = '<p class="empty-cart">Your cart is empty</p>';
            if (footer) footer.style.display = 'none';
            return;
        }
        
        container.innerHTML = items.map((item, index) => `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.title}" onerror="this.src='{% static 'images/placeholder.png' %}'">
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.title}</div>
                    <div class="cart-item-price">₹${item.price}</div>
                    <div class="cart-item-controls">
                        <button class="quantity-btn" onclick="cartManager.updateQuantity('${item.type}_${item.id}', ${item.quantity - 1})">-</button>
                        <input type="number" class="quantity-input" value="${item.quantity}" min="1" 
                               onchange="cartManager.updateQuantity('${item.type}_${item.id}', this.value)">
                        <button class="quantity-btn" onclick="cartManager.updateQuantity('${item.type}_${item.id}', ${item.quantity + 1})">+</button>
                        <span class="remove-item" onclick="cartManager.removeFromCart('${item.type}_${item.id}')">
                            <i class="fas fa-trash"></i>
                        </span>
                    </div>
                </div>
            </div>
        `).join('');
        
        if (footer) {
            footer.style.display = 'block';
            document.getElementById('cartTotal').textContent = `₹${total.toFixed(2)}`;
        }
    }
    
    openCart() {
        this.cartSidebar?.classList.add('active');
        this.cartOverlay?.classList.add('active');
        document.body.style.overflow = 'hidden';
    }
    
    closeCart() {
        this.cartSidebar?.classList.remove('active');
        this.cartOverlay?.classList.remove('active');
        document.body.style.overflow = '';
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed; top: 20px; right: 20px; background: #4CAF50; color: white;
            padding: 14px 24px; border-radius: 8px; z-index: 10000; font-weight: 500;
            transform: translateX(400px); transition: transform 0.3s ease;
        `;
        document.body.appendChild(notification);
        setTimeout(() => notification.style.transform = 'translateX(0)', 100);
        setTimeout(() => {
            notification.style.transform = 'translateX(400px)';
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    }
    
    getCSRFToken() {
        return document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || '';
    }
}

const cartManager = new CartManager();