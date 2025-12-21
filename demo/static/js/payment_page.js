const cartIcon = document.getElementById("cartIcon");
const cartSidebar = document.getElementById("cartSidebar");
const overlay = document.getElementById("cartOverlay");
const closeCartBtn = document.getElementById("closeCartBtn");

cartIcon.addEventListener("click", () => {
    cartSidebar.classList.add("active");
    overlay.classList.add("active");
});

closeCartBtn.addEventListener("click", () => {
    cartSidebar.classList.remove("active");
    overlay.classList.remove("active");
});

overlay.addEventListener("click", () => {
    cartSidebar.classList.remove("active");
    overlay.classList.remove("active");
});
