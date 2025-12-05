// ---------------- Live Search with Dropdown ----------------
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const searchBtn = document.getElementById("searchBtn");
  const dropdown = document.getElementById("searchDropdown");
  
  if (!searchInput || !dropdown) return;
  
  let debounceTimer;
  let currentQuery = "";
  
  // Toggle search bar
  searchBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    searchInput.classList.toggle("active");
    if (searchInput.classList.contains("active")) {
      searchInput.focus();
      dropdown.style.display = "block";
    } else {
      dropdown.style.display = "none";
    }
  });
  
  // Hide dropdown when clicking outside
  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-container")) {
      dropdown.style.display = "none";
      searchInput.classList.remove("active");
    }
  });
  
  // Live search input
  searchInput.addEventListener("input", function() {
    clearTimeout(debounceTimer);
    currentQuery = this.value.trim();
    
    if (currentQuery.length < 2) {
      dropdown.style.display = "none";
      return;
    }
    
    // Show loading
    dropdown.innerHTML = '<div class="search-item loading">Searching...</div>';
    dropdown.style.display = "block";
    
    debounceTimer = setTimeout(() => {
      fetch(`/search/suggestions/?q=${encodeURIComponent(currentQuery)}`)
        .then(response => response.json())
        .then(data => {
          renderDropdownResults(data.results, currentQuery);
        })
        .catch(error => {
          dropdown.style.display = "none";
          console.error("Search error:", error);
        });
    }, 250);
  });
  
  function renderDropdownResults(results, query) {
    dropdown.innerHTML = "";
    
    if (results.length === 0) {
      dropdown.innerHTML = `
        <div class="search-item no-results">
          <i class="fas fa-search" style="font-size: 24px; margin-bottom: 10px; color: #ddd;"></i>
          <div>No books found for "${query}"</div>
        </div>
      `;
      dropdown.style.display = "block";
      return;
    }
    
    results.forEach(item => {
      const resultDiv = document.createElement("div");
      resultDiv.className = "search-item";
      
      // Safe highlight
      const escapeHtml = (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
      };
      
      const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      const safeTitle = escapeHtml(item.title);
      const highlightedTitle = safeTitle.replace(regex, '<strong>$1</strong>');
      
      resultDiv.innerHTML = `
        <img src="${item.image}" alt="" onerror="this.src='{% static 'images/placeholder.png' %}'; this.onerror=null;">
        <div class="search-item-info">
          <div class="search-item-title">${highlightedTitle}</div>
          <div class="search-item-price">Rs. ${escapeHtml(item.price)}</div>
          <div class="search-item-type">${item.type}</div>
        </div>
      `;
      
      resultDiv.addEventListener("click", () => {
        window.location.href = item.url;
      });
      
      dropdown.appendChild(resultDiv);
    });
    
    dropdown.style.display = "block";
  }
});
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
    } else if (text === "Product Categories") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/productcatagory/";
      });
    } else if (text === "About Us") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/aboutus/";
      });
    } else if (text === "Contact Us") {
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
    } else if (text === "Contact Us") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/contactinformation/";
      });
    } else if (text === "Bulk Purchase") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/bulkpurchase/";
      });
    } else if (text === "Return & Replacement") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/return/";
      });
    } else if (text === "Privacy Policy") {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        window.location.href = "/privacy-policy/";
      });
    }
  });
});

// ---------------- View Buttons (REFACTORED) ----------------
document.addEventListener("DOMContentLoaded", function () {
  // Single handler for all view buttons using data attributes
  document.querySelectorAll('.view-btn').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const category = this.getAttribute('data-category');
      if (category) {
        window.location.href = `/category/${category}/`;
      }
    });
  });
});

// ---------------- Quantity Counter ----------------
document.addEventListener("DOMContentLoaded", () => {
  const qtyDisplay = document.getElementById('qty');
  const plus = document.getElementById('plus');
  const minus = document.getElementById('minus');
  if (!qtyDisplay || !plus || !minus) return;
  
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
  if (!pagination) return;

  const prevBtn = pagination.querySelector(".prev");
  const nextBtn = pagination.querySelector(".next");
  const dots = pagination.querySelector(".dots");
  const totalPages = 42;
  let currentPage = 1;

  function renderPagination() {
    pagination.querySelectorAll(".page").forEach(p => p.remove());
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

    dots.style.display = pagesToShow.includes(totalPages) ? "none" : "inline";
    prevBtn.classList.toggle("disabled", currentPage === 1);
    nextBtn.classList.toggle("disabled", currentPage === totalPages);
  }

  function getPagesToShow(current, total) {
    if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1);
    if (current <= 3) return [1, 2, 3];
    if (current >= total - 2) return [total - 2, total - 1, total];
    return [current - 1, current, current + 1];
  }

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