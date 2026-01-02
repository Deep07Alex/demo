// static/js/checkout.js - Email OTP & Checkout Flow

document.addEventListener('DOMContentLoaded', function() {
    // DOM References
    const emailInput = document.getElementById('emailInput');
    const sendOtpBtn = document.getElementById('sendOtpBtn');
    const otpSection = document.getElementById('otpSection');
    const otpInput = document.getElementById('otpInput');
    const verifyOtpBtn = document.getElementById('verifyOtpBtn');
    const otpMessage = document.getElementById('otpMessage');
    const addressSection = document.getElementById('addressSection');
    const pincodeInput = document.getElementById('pincode');
    const shippingOptions = document.getElementById('shippingOptions');
    const shippingLoading = document.getElementById('shippingLoading');
    const shippingError = document.getElementById('shippingError');
    const errorMessage = document.getElementById('errorMessage');
    const proceedToPaymentBtn = document.getElementById('proceedToPaymentBtn');
    const orderSummary = document.getElementById('orderSummary');

    // If we are NOT on the checkout page (elements missing), do nothing
    if (!emailInput || !sendOtpBtn || !otpSection || !pincodeInput || !orderSummary) {
        return;
    }

    let selectedShippingRate = null;
    let isEmailVerified = false;


    // =========================================================================
    // EMAIL VERIFICATION
    // =========================================================================
    
    sendOtpBtn.addEventListener('click', async function() {
        const email = emailInput.value.trim();
        
        if (!email || !email.includes('@')) {
            alert('Please enter a valid email address');
            return;
        }
        
        sendOtpBtn.disabled = true;
        sendOtpBtn.textContent = 'Sending...';
        
        try {
            const response = await fetch('/api/send-email-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ email: email })
            });
            
            const data = await response.json();
            
            if (data.success) {
                otpSection.classList.remove('hidden');
                otpMessage.textContent = 'OTP sent to your email!';
                otpMessage.className = 'text-sm mt-2 text-green-600';
                otpInput.focus();
            } else {
                otpMessage.textContent = data.error || 'Failed to send OTP';
                otpMessage.className = 'text-sm mt-2 text-red-600';
            }
        } catch (error) {
            otpMessage.textContent = 'Network error. Try again.';
            otpMessage.className = 'text-sm mt-2 text-red-600';
        } finally {
            sendOtpBtn.disabled = false;
            sendOtpBtn.textContent = 'Send OTP';
        }
    });
    
    verifyOtpBtn.addEventListener('click', async function() {
        const email = emailInput.value.trim();
        const otp = otpInput.value.trim();
        
        if (otp.length !== 6) {
            otpMessage.textContent = 'Please enter 6-digit OTP';
            otpMessage.className = 'text-sm mt-2 text-red-600';
            return;
        }
        
        verifyOtpBtn.disabled = true;
        verifyOtpBtn.textContent = 'Verifying...';
        
        try {
            const response = await fetch('/api/verify-email-otp/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ email: email, otp: otp })
            });
            
            const data = await response.json();
            
            if (data.success) {
                isEmailVerified = true;
                otpMessage.textContent = '✓ Email verified successfully!';
                otpMessage.className = 'text-sm mt-2 text-green-600';
                
                // Unlock address section
                addressSection.classList.remove('opacity-50', 'pointer-events-none');
                
                // Disable email field and OTP section
                emailInput.disabled = true;
                sendOtpBtn.disabled = true;
                otpInput.disabled = true;
                verifyOtpBtn.disabled = true;
                
                // Load order summary
                loadOrderSummary();
            } else {
                otpMessage.textContent = data.error || 'Invalid OTP';
                otpMessage.className = 'text-sm mt-2 text-red-600';
            }
        } catch (error) {
            otpMessage.textContent = 'Verification failed. Try again.';
            otpMessage.className = 'text-sm mt-2 text-red-600';
        } finally {
            verifyOtpBtn.disabled = false;
            verifyOtpBtn.textContent = 'Verify';
        }
    });

    // =========================================================================
    // SHIPPING CALCULATION
    // =========================================================================
    
    pincodeInput.addEventListener('blur', function() {
        const pincode = this.value.trim();
        if (pincode.length === 6 && isEmailVerified) {
            calculateShipping(pincode);
        }
    });
    
    async function calculateShipping(pincode) {
      shippingLoading.classList.remove("hidden");
      shippingError.classList.add("hidden");
      shippingOptions.innerHTML = "";
      proceedToPaymentBtn.disabled = true;

      try {
        const response = await fetch("/api/calculate-shipping/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({ pincode: pincode }),
        });

        const data = await response.json();
        shippingLoading.classList.add("hidden");

        if (data.success) {
          displayShippingOptions(data.rates); // NO error call here
        } else {
          showShippingError(data.error); // keep this
        }
      } catch (error) {
        shippingLoading.classList.add("hidden");
        // REMOVE this line so the red banner never shows on network error:
        // showShippingError('Unable to calculate shipping');
        console.error("Shipping error:", error);
      }
    }

    
    function displayShippingOptions(rates) {
        if (!rates || rates.length === 0) {
            showShippingError('No shipping options available');
            return;
        }
        
        shippingOptions.innerHTML = rates.map((rate, index) => `
            <label class="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-[#e20074] cursor-pointer transition-colors ${index === 0 ? 'border-[#e20074] bg-pink-50' : ''}">
                <input type="radio" name="shipping_option" value="${index}" 
                       data-rate='${JSON.stringify(rate)}'
                       ${index === 0 ? 'checked' : ''}
                       class="mr-4 text-[#e20074] focus:ring-[#e20074]">
                <div class="flex-1">
                    <div class="flex justify-between items-start">
                        <div>
                            <div class="font-semibold text-gray-800">${rate.courier_name}</div>
                            <div class="text-sm text-gray-600 mt-1">Est. delivery: ${rate.estimated_days} days</div>
                        </div>
                        <div class="text-right">
                            <div class="font-bold text-lg text-[#e20074]">₹${rate.total_charge.toFixed(2)}</div>
                        </div>
                    </div>
                </div>
            </label>
        `).join('');
        
        // Add event listeners
        document.querySelectorAll('input[name="shipping_option"]').forEach(radio => {
            radio.addEventListener('change', function() {
                document.querySelectorAll('.shipping-option-card').forEach(card => {
                    card.classList.remove('border-[#e20074]', 'bg-pink-50');
                });
                this.closest('label').classList.add('border-[#e20074]', 'bg-pink-50');
                
                selectedShippingRate = JSON.parse(this.dataset.rate);
                updateTotalAmount();
            });
        });
        
        // Auto-select first option
        selectedShippingRate = rates[0];
        updateTotalAmount();
        proceedToPaymentBtn.disabled = false;
        
        // Add class for styling
        document.querySelectorAll('#shippingOptions label').forEach(label => {
            label.classList.add('shipping-option-card');
        });
    }
    
    function showShippingError(message) {
        shippingError.classList.remove('hidden');
        errorMessage.textContent = message;
        
        // Still allow proceeding with default shipping
        proceedToPaymentBtn.disabled = false;
    }
    
    function updateTotalAmount() {
        if (!selectedShippingRate) return;
        
        const shippingCost = selectedShippingRate.total_charge;
        document.getElementById('shippingCost').textContent = `₹${shippingCost.toFixed(2)}`;
        
        // Recalculate total
        const subtotal = parseFloat(document.getElementById('subtotal').textContent.replace('₹', ''));
        const discount = parseFloat(document.getElementById('discount').textContent.replace('₹', ''));
        const total = subtotal + shippingCost - discount;
        document.getElementById('totalAmount').textContent = `₹${total.toFixed(2)}`;
        
        // Update button text
        proceedToPaymentBtn.innerHTML = `<i class="fas fa-lock mr-2"></i>Pay ₹${total.toFixed(2)}`;
    }

    // =========================================================================
    // ORDER SUMMARY
    // =========================================================================
    
    function loadOrderSummary() {
        fetch('/cart/items/')
            .then(response => response.json())
            .then(data => {
                if (data.success !== false) {
                    renderOrderSummary(data);
                }
            });
    }
    
    function renderOrderSummary(data) {
    const summaryEl = document.getElementById('orderSummary');
    const subtotalEl = document.getElementById('subtotal');
    const shippingEl = document.getElementById('shippingCost');
    const discountEl = document.getElementById('discount');
    const totalEl = document.getElementById('totalAmount');

    if (!data.items || data.items.length === 0) {
        summaryEl.innerHTML = '<p class="text-gray-500">Cart is empty</p>';
        return;
    }

    summaryEl.innerHTML = data.items.map(item => `
        <div class="flex items-center space-x-3 text-sm">
            <img src="${item.image}" alt="${item.title}"
                 class="w-10 h-10 object-cover rounded"
                 onerror="this.src='/static/images/placeholder.png'">
            <div class="flex-1">
                <p class="font-medium truncate">${item.title}</p>
                <p class="text-gray-500">Qty: ${item.quantity} × ₹${parseFloat(item.price).toFixed(2)}</p>
            </div>
        </div>
    `).join('');

    subtotalEl.textContent = `₹${parseFloat(data.total).toFixed(2)}`;
    shippingEl.textContent = `₹${parseFloat(data.shipping).toFixed(2)}`;
    discountEl.textContent = `₹${parseFloat(data.discount).toFixed(2)}`;
    totalEl.textContent = `₹${(parseFloat(data.total) + parseFloat(data.shipping) - parseFloat(data.discount)).toFixed(2)}`;
}


    // =========================================================================
    // PROCEED TO PAYMENT
    // =========================================================================
    
     proceedToPaymentBtn.addEventListener('click', async function() {
        if (!isEmailVerified) {
          alert("Please verify your email first");
          return;
        }

        if (!selectedShippingRate) {
          alert("Please calculate shipping rates first");
          return;
        }
        
        const formData = {
        fullname: document.getElementById('fullname').value,
        phone: document.getElementById('phone').value,
        address: document.getElementById('address').value,
        city: document.getElementById('city').value,
        state: document.getElementById('state').value,
        pincode: document.getElementById('pincode').value,
        delivery: 'Standard (3-6 days)',
        payment_method: 'card',
        shipping_cost: selectedShippingRate.total_charge,  
        courier_name: selectedShippingRate.courier_name,
        estimated_days: selectedShippingRate.estimated_days
    };
        
        // Validate
        const requiredFields = ['fullname', 'phone', 'address', 'city', 'state', 'pincode'];
        for (let field of requiredFields) {
            if (!formData[field]) {
                alert(`Please fill ${field} field`);
                return;
            }
        }
        
        proceedToPaymentBtn.disabled = true;
        proceedToPaymentBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Processing...';
        
        try {
            const response = await fetch('/api/initiate-payment/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify(formData)
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
                proceedToPaymentBtn.disabled = false;
                proceedToPaymentBtn.innerHTML = '<i class="fas fa-lock mr-2"></i>Proceed to Payment';
            }
        } catch (error) {
            alert('Network error: ' + error.message);
            proceedToPaymentBtn.disabled = false;
            proceedToPaymentBtn.innerHTML = '<i class="fas fa-lock mr-2"></i>Proceed to Payment';
        }
    });

    // =========================================================================
    // UTILITY FUNCTIONS
    // =========================================================================
    
    function getCSRFToken() {
        const token = document.cookie.match(/csrftoken=([\w-]+)/)?.[1] || "";
        return token;
    }

    // Load initial data
    loadOrderSummary();
});