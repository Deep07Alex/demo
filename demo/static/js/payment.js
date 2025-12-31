document.addEventListener("DOMContentLoaded", () => {
  class DirectPaymentManager {
    constructor() {
      this.modal = null;
      this.overlay = null;
      this.isProcessing = false;
      this.currentVerificationId = null;
      this.shippingRates = [];
      this.selectedShipping = null;
      this.init();
    }

    init() {
      this.createPaymentModal();
      this.attachEventListeners();
    }

    createPaymentModal() {
      // Create modal HTML structure with shipping calculator
      const modalHTML = `
        <div id="paymentModalOverlay" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden"></div>
        <div id="paymentModal" class="fixed inset-0 z-50 flex items-center justify-center p-4 hidden">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div class="p-6 border-b">
              <h2 class="text-xl font-semibold">Complete Your Order</h2>
              <p class="text-sm text-gray-600">Verify email and enter shipping details</p>
            </div>
            
            <div class="p-6 space-y-4">
              <!-- Email Verification -->
              <div class="bg-gray-50 p-4 rounded-lg">
                <h3 class="font-medium mb-3">1. Verify Email</h3>
                <div class="flex gap-2">
                  <input type="email" id="modalEmailInput" placeholder="your@email.com" 
                         class="flex-1 px-3 py-2 border rounded-lg text-sm">
                  <button id="modalSendCodeBtn" class="bg-[#e20074] text-white px-4 py-2 rounded-lg text-sm font-medium">
                    Send Code
                  </button>
                </div>
                <div id="modalTokenSection" class="mt-3 hidden">
                  <input type="text" id="modalTokenInput" placeholder="Enter 6-digit code"
                         class="w-full px-3 py-2 border rounded-lg text-sm mb-2">
                  <div class="flex justify-between items-center">
                    <button id="modalVerifyBtn" class="bg-green-600 text-white px-4 py-2 rounded-lg text-sm">
                      Verify
                    </button>
                    <button id="modalResendBtn" class="text-[#e20074] text-sm hover:underline">
                      Resend Code
                    </button>
                  </div>
                </div>
                <p id="modalTokenHint" class="text-sm mt-2"></p>
              </div>

              <!-- Shipping Address -->
              <div id="modalAddressSection" class="opacity-50 pointer-events-none space-y-3">
                <h3 class="font-medium">2. Shipping Address</h3>
                <div class="grid grid-cols-2 gap-3">
                  <input type="text" id="modalFullName" placeholder="Full Name" class="px-3 py-2 border rounded-lg text-sm col-span-2">
                  <input type="tel" id="modalPhone" placeholder="Mobile Number" class="px-3 py-2 border rounded-lg text-sm col-span-2">
                </div>
                <textarea id="modalAddress" placeholder="House, Street, Landmark" 
                          class="w-full px-3 py-2 border rounded-lg text-sm h-20"></textarea>
                <div class="grid grid-cols-2 gap-3">
                  <input type="text" id="modalCity" placeholder="City" class="px-3 py-2 border rounded-lg text-sm">
                  <input type="text" id="modalState" placeholder="State" class="px-3 py-2 border rounded-lg text-sm">
                </div>
                <div class="grid grid-cols-2 gap-3">
                  <input type="text" id="modalPin" placeholder="PIN Code" class="px-3 py-2 border rounded-lg text-sm">
                  <button type="button" id="calculateShippingBtn" 
                          class="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm">
                    Calculate Shipping
                  </button>
                </div>
                
                <!-- Shipping Rates Display -->
                <div id="shippingRatesSection" class="hidden">
                  <h4 class="font-medium text-sm mb-2">Available Shipping Options:</h4>
                  <div id="shippingRatesList" class="space-y-2">
                    <!-- Shipping rates will be populated here -->
                  </div>
                </div>
              </div>
            </div>

            <div class="p-6 border-t flex justify-between items-center">
              <div>
                <p class="text-sm text-gray-500">Order Total</p>
                <p class="text-xl font-bold">₹<span id="modalTotalAmount">0.00</span></p>
              </div>
              <button id="modalPayBtn" disabled 
                      class="bg-[#e20074] text-white px-6 py-3 rounded-lg font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed">
                    Verify Email to Pay
              </button>
            </div>
          </div>
        </div>
      `;
      
      document.body.insertAdjacentHTML('beforeend', modalHTML);
      this.modal = document.getElementById('paymentModal');
      this.overlay = document.getElementById('paymentModalOverlay');
    }

    attachEventListeners() {
      // Cart checkout button
      const checkoutBtn = document.querySelector('.checkout-btn');
      if (checkoutBtn) {
        checkoutBtn.addEventListener('click', (e) => {
          e.preventDefault();
          this.openPaymentModal();
        });
      }

      // Modal events
      document.getElementById('modalSendCodeBtn').addEventListener('click', () => this.sendVerification());
      document.getElementById('modalVerifyBtn').addEventListener('click', () => this.verifyToken());
      document.getElementById('modalResendBtn').addEventListener('click', () => this.resendToken());
      document.getElementById('modalPayBtn').addEventListener('click', () => this.processPayment());
      document.getElementById('calculateShippingBtn').addEventListener('click', () => this.calculateShipping());
      
      // Close modal
      this.overlay.addEventListener('click', () => this.closeModal());
    }

    async calculateShipping() {
      const pincode = document.getElementById('modalPin').value.trim();
      const btn = document.getElementById('calculateShippingBtn');
      
      if (!pincode || pincode.length !== 6) {
        this.showModalHint('Please enter a valid 6-digit PIN code', 'error');
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Calculating...';

      try {
        const response = await fetch('/api/calculate-shipping/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          body: JSON.stringify({ pincode: pincode }),
        });

        const data = await response.json();
        
        if (data.success) {
          this.displayShippingRates(data.rates);
          this.showModalHint('Shipping rates calculated successfully', 'success');
        } else {
          this.showModalHint(data.error || 'Unable to calculate shipping', 'error');
        }
      } catch (error) {
        this.showModalHint('Network error calculating shipping', 'error');
      } finally {
        btn.disabled = false;
        btn.textContent = 'Calculate Shipping';
      }
    }

    displayShippingRates(rates) {
      const ratesSection = document.getElementById('shippingRatesSection');
      const ratesList = document.getElementById('shippingRatesList');
      
      ratesList.innerHTML = '';
      
      rates.forEach((rate, index) => {
        const rateElement = document.createElement('div');
        rateElement.className = 'shipping-option p-3 border rounded-lg cursor-pointer hover:bg-gray-50';
        rateElement.innerHTML = `
          <div class="flex justify-between items-center">
            <div>
              <div class="font-medium text-sm">${rate.courier_name}</div>
              <div class="text-xs text-gray-600">Delivery: ${rate.estimated_days} days</div>
            </div>
            <div class="text-right">
              <div class="font-semibold text-sm">₹${rate.total_charge.toFixed(2)}</div>
              <input type="radio" name="shipping_option" value="${index}" 
                     ${index === 0 ? 'checked' : ''} class="mt-1">
            </div>
          </div>
        `;
        
        rateElement.addEventListener('click', () => {
          this.selectShippingOption(index, rate);
          // Check the radio button
          rateElement.querySelector('input[type="radio"]').checked = true;
        });
        
        ratesList.appendChild(rateElement);
      });
      
      ratesSection.classList.remove('hidden');
      
      // Auto-select first option
      if (rates.length > 0) {
        this.selectShippingOption(0, rates[0]);
      }
    }

    selectShippingOption(index, rate) {
      this.selectedShipping = rate;
      this.updateTotalAmount();
    }

    updateTotalAmount() {
      const baseTotal = parseFloat(document.getElementById('cartTotal').textContent.replace('₹', ''));
      let shippingCost = 0;
      
      if (this.selectedShipping) {
        shippingCost = this.selectedShipping.total_charge;
      }
      
      const finalTotal = baseTotal + shippingCost;
      document.getElementById('modalTotalAmount').textContent = finalTotal.toFixed(2);
      
      // Update pay button text
      const payBtn = document.getElementById('modalPayBtn');
      if (!payBtn.disabled) {
        payBtn.textContent = `Pay ₹${finalTotal.toFixed(2)}`;
      }
    }

    openPaymentModal() {
      this.overlay.classList.remove('hidden');
      this.modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      
      // Update total amount
      const totalEl = document.getElementById('cartTotal');
      document.getElementById('modalTotalAmount').textContent = totalEl.textContent.replace('₹', '');
    }

    closeModal() {
      this.overlay.classList.add('hidden');
      this.modal.classList.add('hidden');
      document.body.style.overflow = '';
    }

    // ... rest of your existing methods (sendVerification, verifyToken, etc.) ...

    async processPayment() {
      if (this.isProcessing) return;
      
      if (!this.selectedShipping) {
        alert('Please calculate shipping rates first');
        return;
      }
      
      this.isProcessing = true;

      const payBtn = document.getElementById('modalPayBtn');
      payBtn.disabled = true;
      payBtn.textContent = 'Processing...';

      const orderData = {
        phone: document.getElementById('modalPhone').value,
        fullname: document.getElementById('modalFullName').value,
        email: document.getElementById('modalEmailInput').value,
        address: document.getElementById('modalAddress').value,
        city: document.getElementById('modalCity').value,
        state: document.getElementById('modalState').value,
        pin: document.getElementById('modalPin').value,
        delivery: document.getElementById('modalDelivery').value,
        shipping_option: this.selectedShipping,
      };

      // Validation
      if (!orderData.fullname || !orderData.email || !orderData.phone || !orderData.address) {
        alert('Please fill all required fields');
        this.isProcessing = false;
        payBtn.disabled = false;
        payBtn.textContent = 'Pay';
        return;
      }

      try {
        const response = await fetch('/api/initiate-payment/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
          },
          body: JSON.stringify(orderData),
        });

        const data = await response.json();
        if (data.success) {
          // Submit to PayU
          const form = document.createElement('form');
          form.method = 'POST';
          form.action = data.payu_url;
          form.style.display = 'none';

          Object.entries(data.payu_params).forEach(([key, value]) => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = value;
            form.appendChild(input);
          });

          document.body.appendChild(form);
          form.submit();
        } else {
          alert('Payment error: ' + data.error);
        }
      } catch (error) {
        alert('Network error: ' + error.message);
      } finally {
        this.isProcessing = false;
        payBtn.disabled = false;
        payBtn.textContent = 'Pay';
      }
    }

    showModalHint(message, type) {
      const hint = document.getElementById('modalTokenHint');
      hint.textContent = message;
      hint.style.color = type === 'success' ? '#10b981' : '#ef4444';
    }
  }

  // Initialize
  window.directPaymentManager = new DirectPaymentManager();
});