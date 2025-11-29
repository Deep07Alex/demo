// ---------------- Header Navigation ----------------
document.addEventListener("DOMContentLoaded", function () {
  const links = document.querySelectorAll(".nav-links a");

  links.forEach(link => {
    const text = link.textContent.trim();

    if (text === "Home") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/";
      });
    } 

    else if (text === "Product Categories") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/productcatagory/";
      });
    } 

    else if (text === "About Us") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/aboutus/";
      });
    }

    else if (text === "Contact Us") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/contactinformation/";
      });
    }
  });
});


// ---------------- Footer Navigation ----------------
document.addEventListener("DOMContentLoaded", function () {
  const footerLinks = document.querySelectorAll(".footer-section ul li a");

  footerLinks.forEach(link => {
    const text = link.textContent.trim();

    if (text === "About Us") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/aboutus/";
      });
    } 

    else if (text === "Contact Us") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/contactinformation/";
      });
    } 

    else if (text === "Bulk Purchase") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/bulkpurchase/";
      });
    } 

    else if (text === "Return & Replacement") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/return/";
      });
    } 

    else if (text === "Privacy Policy") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/privacy-policy/";
      });
    } 
  });
});


// ---------------- View Buttons ----------------
document.addEventListener("DOMContentLoaded", function () {
  const saleBtn = document.querySelector("#btn1");
  const romanceBtn = document.querySelector("#btn2");
  const trading_financebtn = document.querySelector("#btn3");  
  const mangabtn = document.querySelector("#btn4");
  const Mythologybtn = document.querySelector("#btn5");
  const Hindibtn = document.querySelector("#btn6");
  const Prelovedbtn = document.querySelector("#btn7");
  const newbtn = document.querySelector("#btn8");
  const combobtn = document.querySelector("#btn9");




  if (saleBtn) {
    saleBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/sale/"; 
    });
  }

  if (romanceBtn) {
    romanceBtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/romance/"; 
    });
  }

  if (trading_financebtn) {  
    trading_financebtn.addEventListener("click", function (e) { 
      e.preventDefault();
      window.location.href = "/trading-finance/";  
    });
  }

  if (mangabtn) {
    mangabtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/manga/"; 
    });
  }

  if (Mythologybtn) {
    Mythologybtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/Mythology/"; 
    });
  }

  if (Hindibtn) {
    Hindibtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/Hindi/"; 
    });
  }

  if (Prelovedbtn) {
    Prelovedbtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/Preloved/"; 
    });
  }

  if (newbtn) {
    newbtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/new/"; 
    });
  }

  if (combobtn) {
    combobtn.addEventListener("click", function (e) {
      e.preventDefault();
      window.location.href = "/combo/"; 
    });
  }
});



// Add to cart button




// Quantity Counter banner
document.addEventListener("DOMContentLoaded", () => {
  const qtyDisplay = document.getElementById('qty');
  const plus = document.getElementById('plus');
  const minus = document.getElementById('minus');
  let quantity = 1;

  plus.addEventListener('click', () => {
    quantity++;
    qtyDisplay.textContent = quantity;
  });

  minus.addEventListener('click', () => {
    if (quantity > 1) {
      quantity--;
      qtyDisplay.textContent = quantity;
    }
  });
});





// ---------------- Pagination ----------------
document.addEventListener("DOMContentLoaded", function () {
  const pagination = document.querySelector(".pagination");
  if (!pagination) return; // Stop if pagination element is missing

  const prevBtn = pagination.querySelector(".prev");
  const nextBtn = pagination.querySelector(".next");
  const dots = pagination.querySelector(".dots");
  const totalPages = 42;
  let currentPage = 1;

  // Render pagination numbers dynamically
  function renderPagination() {
    // Remove all existing number links except arrows and dots
    pagination.querySelectorAll(".page").forEach(p => p.remove());

    // Insert new number elements before dots
    const beforeDots = dots;
    const pagesToShow = getPagesToShow(currentPage, totalPages);

    pagesToShow.forEach(pageNum => {
      const a = document.createElement("a");
      a.href = "#";
      a.textContent = pageNum;
      a.classList.add("page");
      if (pageNum === currentPage) a.classList.add("active");
      beforeDots.before(a);
    });

    // Show or hide dots
    dots.style.display = pagesToShow.includes(totalPages) ? "none" : "inline";

    // Disable prev/next when at limits
    prevBtn.classList.toggle("disabled", currentPage === 1);
    nextBtn.classList.toggle("disabled", currentPage === totalPages);
  }

  // Decide which pages to show
  function getPagesToShow(current, total) {
    if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1);
    if (current <= 3) return [1, 2, 3];
    if (current >= total - 2) return [total - 2, total - 1, total];
    return [current - 1, current, current + 1];
  }

  // Handle clicks
  pagination.addEventListener("click", e => {
    e.preventDefault();

    if (e.target.classList.contains("page")) {
      currentPage = parseInt(e.target.textContent);
      renderPagination();
    }

    if (e.target.classList.contains("next") && currentPage < totalPages) {
      currentPage++;
      renderPagination();
    }

    if (e.target.classList.contains("prev") && currentPage > 1) {
      currentPage--;
      renderPagination();
    }
  });

  renderPagination();
});
