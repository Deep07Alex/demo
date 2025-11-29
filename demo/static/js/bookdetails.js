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

// Countdown Timer (fixed 12-hour timer)
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
