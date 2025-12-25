// Quantity Controls
function increaseQty() {
    let q = document.getElementById("qty-display");
    q.innerText = parseInt(q.innerText) + 1;
}

function decreaseQty() {
    let q = document.getElementById("qty-display");
    if (parseInt(q.innerText) > 1) {
        q.innerText = parseInt(q.innerText) - 1;
    }
}

// Buy Now - Simplified and Robust
document.addEventListener("DOMContentLoaded", function() {
    const buyNowBtn = document.querySelector('.buy-now');
    
    if (buyNowBtn) {
        console.log("✅ Buy Now button found and listener attached");
        
        buyNowBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const bookId = this.dataset.id;
            const title = this.dataset.title;
            const price = this.dataset.price;
            const image = this.dataset.image;
            const quantity = parseInt(document.getElementById("qty-display").innerText);
            
            console.log('🛒 Buy Now initiated:', { bookId, title, quantity });
            
            try {
                // Clear existing cart first
                await fetch('/cart/clear/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    }
                });
                
                // Add the book
                const addResponse = await fetch('/cart/add/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken()
                    },
                    body: JSON.stringify({
                        id: bookId,
                        type: 'book',
                        title: title,
                        price: price,
                        image: image
                    })
                });
                
                const addData = await addResponse.json();
                console.log('✅ Book added:', addData);
                
                // Update quantity if needed
                if (quantity > 1) {
                    await fetch('/cart/update/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'X-CSRFToken': getCSRFToken()
                        },
                        body: JSON.stringify({
                            key: `book_${bookId}`,
                            quantity: quantity
                        })
                    });
                }
                
                // Redirect to checkout
                console.log('🔄 Redirecting to checkout...');
                window.location.href = '/checkout/';
                
            } catch (error) {
                console.error('❌ Buy Now error:', error);
                alert('Error: ' + error.message);
            }
        });
    } else {
        console.warn("⚠️ Buy Now button not found on page");
    }
});

// Countdown Timer
let countDownDate = new Date().getTime() + 12 * 60 * 60 * 1000;
setInterval(function () {
    let now = new Date().getTime();
    let distance = countDownDate - now;

    let hrs = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    let mins = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    let secs = Math.floor((distance % (1000 * 60)) / 1000);

    document.getElementById("hrs").innerHTML = hrs;
    document.getElementById("mins").innerHTML = mins;
    document.getElementById("secs").innerHTML = secs;

    if (distance < 0) {
        document.getElementById("countdown").innerHTML = "Expired";
    }
}, 1000);

// CSRF Token Helper
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) return metaTag.content;
    
    const cookie = document.cookie.match(/csrftoken=([\w-]+)/);
    if (cookie) return cookie[1];
    
    console.warn("⚠️ CSRF token not found!");
    return '';
}