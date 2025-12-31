// ============================================
// Hero Section Slider (FULLY FIXED)
// ============================================
const slides = document.getElementById("slides");
const dotsContainer = document.getElementById("pagination");

if (slides && dotsContainer) {
  const slideCount = slides.children.length;
  let index = 0;
  let interval;

  // Create dots
  dotsContainer.innerHTML = "";
  for (let i = 0; i < slideCount; i++) {
    const dot = document.createElement("div");
    dot.className = "dot" + (i === 0 ? " active" : "");
    dot.addEventListener("click", () => goToSlide(i));
    dotsContainer.appendChild(dot);
  }

  function updateSlider() {
    slides.style.transform = `translateX(-${index * 100}%)`;
    document.querySelectorAll(".dot").forEach((dot, i) => {
      dot.classList.toggle("active", i === index);
    });
  }

  function nextSlide() {
    index = (index + 1) % slideCount;
    updateSlider();
  }

  function prevSlide() {
    index = (index - 1 + slideCount) % slideCount;
    updateSlider();
  }

  function goToSlide(i) {
    index = i;
    updateSlider();
    resetAuto();
  }

  function startAuto() {
    interval = setInterval(nextSlide, 4000);
  }

  function resetAuto() {
    clearInterval(interval);
    startAuto();
  }

  // Init
  updateSlider();
  startAuto();

  window.nextSlide = nextSlide;
  window.prevSlide = prevSlide;

  // Swipe touch support
  const sliderElement = document.querySelector(".slider");
  if (sliderElement) {
    let startX = 0;
    let endX = 0;

    sliderElement.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
    }, { passive: true });

    sliderElement.addEventListener("touchmove", (e) => {
      endX = e.touches[0].clientX;
    }, { passive: true });

    sliderElement.addEventListener("touchend", () => {
      const swipeDistance = startX - endX;
      if (swipeDistance > 50) nextSlide();
      else if (swipeDistance < -50) prevSlide();
    });
  }
}



// swipe touch

  const slider = document.querySelector(".slider");
  let startX = 0;
  let endX = 0;

  slider.addEventListener("touchstart", (e) => {
    startX = e.touches[0].clientX;
  }, { passive: true });

  slider.addEventListener("touchmove", (e) => {
    endX = e.touches[0].clientX;
  }, { passive: true });

  slider.addEventListener("touchend", () => {
    const swipeDistance = startX - endX;

    if (swipeDistance > 50) {
      nextSlide(); // swipe left
    } else if (swipeDistance < -50) {
      prevSlide(); // swipe right
    }
  });




// ============================================
// Advertisement Slider
// ============================================
let adIndex = 0;
const adSlides = document.getElementById("adSlides");

if (adSlides) {
  const totalAds = adSlides.children.length;
  function updateAd() {
    adSlides.style.transform = `translateX(-${adIndex * 100}%)`;
  }
  function nextAd() {
    adIndex = (adIndex + 1) % totalAds;
    updateAd();
  }
  function prevAd() {
    adIndex = (adIndex - 1 + totalAds) % totalAds;
    updateAd();
  }
  setInterval(nextAd, 3000);
  window.nextAd = nextAd;
  window.prevAd = prevAd;
}

// ============================================
// Live Search with Dropdown
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("searchInput");
  const searchBtn = document.getElementById("searchBtn");
  const dropdown = document.getElementById("searchDropdown");

  if (!searchInput || !dropdown) return;

  let debounceTimer;
  let currentQuery = "";

  searchBtn?.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    searchInput.classList.toggle("active");
    dropdown.style.display = searchInput.classList.contains("active") ? "block" : "none";
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".search-container")) {
      dropdown.style.display = "none";
      searchInput.classList.remove("active");
    }
  });

  searchInput.addEventListener("input", function () {
    clearTimeout(debounceTimer);
    currentQuery = this.value.trim();
    if (currentQuery.length < 2) {
      dropdown.style.display = "none";
      return;
    }

    dropdown.innerHTML = '<div class="search-item loading">Searching...</div>';
    dropdown.style.display = "block";

    debounceTimer = setTimeout(() => {
      fetch(`/search/suggestions/?q=${encodeURIComponent(currentQuery)}`)
        .then((response) => response.json())
        .then((data) => {
          renderDropdownResults(data.results, currentQuery);
        })
        .catch((error) => {
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
        </div>`;
      dropdown.style.display = "block";
      return;
    }

    results.forEach((item) => {
      const resultDiv = document.createElement("div");
      resultDiv.className = "search-item";
      const escapeHtml = (text) => {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
      };
      const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi");
      const safeTitle = escapeHtml(item.title);
      const highlightedTitle = safeTitle.replace(regex, "<strong>$1</strong>");

      resultDiv.innerHTML = `
        <img src="${item.image}" alt="" onerror="this.src='/static/images/placeholder.png'; this.onerror=null;">
        <div class="search-item-info">
          <div class="cart-item-title">${highlightedTitle}</div>
          <div class="cart-item-price">Rs. ${escapeHtml(item.price)}</div>
          <div class="cart-item-type">${item.type}</div>
        </div>`;

      resultDiv.addEventListener("click", () => {
        window.location.href = item.url;
      });
      dropdown.appendChild(resultDiv);
    });
    dropdown.style.display = "block";
  }
});

// ============================================
// Header & Footer Navigation
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  // Header links
  const links = document.querySelectorAll(".nav-links a");
  links.forEach((link) => {
    const text = link.textContent.trim();
    if (!text) return;
    if (text === "Home") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/"; });
    else if (text === "Product Categories") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/productcatagory/"; });
    else if (text === "Bulk Purchase") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/bulkpurchase/"; });
    else if (text === "About Us") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/aboutus/"; });
    else if (text === "Return & Replacement") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/return/"; });
    else if (text === "Contact Us") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/contactinformation/"; });
    else if (text === "Privacy Policy") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/privacy-policy/"; });
  });

  // Footer links
  const footerLinks = document.querySelectorAll(".footer-section ul li a");
  footerLinks.forEach((link) => {
    const text = link.textContent.trim();
    if (!text) return;
    if (text === "About Us") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/aboutus/"; });
    else if (text === "Contact Us") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/contactinformation/"; });
    else if (text === "Bulk Purchase") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/bulkpurchase/"; });
    else if (text === "Return & Replacement") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/return/"; });
    else if (text === "Privacy Policy") link.addEventListener("click", (e) => { e.preventDefault(); window.location.href = "/privacy-policy/"; });
  });
});

// ============================================
// View Buttons
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".view-btn").forEach((button) => {
    button.addEventListener("click", function (e) {
      e.preventDefault();
      const category = this.getAttribute("data-category");
      if (category) {
        window.location.href = `/category/${category}/`;
      }
    });
  });
});

// ============================================
// Quantity Counter
// ============================================
document.addEventListener("DOMContentLoaded", () => {
  const qtyDisplay = document.getElementById("qty-display");
  const plus = document.getElementById("plus");
  const minus = document.getElementById("minus");

  if (!qtyDisplay || !plus || !minus) return;

  let quantity = 1;
  plus.addEventListener("click", () => {
    quantity++;
    qtyDisplay.textContent = quantity;
  });
  minus.addEventListener("click", () => {
    if (quantity > 1) {
      quantity--;
      qtyDisplay.textContent = quantity;
    }
  });
});

// ============================================
// Hamburger Sidebar Toggle
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  const hamburger = document.getElementById("hamburger");
  const sidebar = document.getElementById("sidebar");
  const closeSidebar = document.getElementById("closeSidebar");

  if (!hamburger || !sidebar || !closeSidebar) return;

  hamburger.addEventListener("click", () => sidebar.classList.add("active"));
  closeSidebar.addEventListener("click", () => sidebar.classList.remove("active"));
  document.addEventListener("click", (e) => {
    if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
      sidebar.classList.remove("active");
    }
  });
});

// ============================================
// Mobile Pagination Dots
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  if (window.innerWidth > 768) return;

  const bookSections = document.querySelectorAll(".book-sale");
  bookSections.forEach((section) => {
    const grid = section.querySelector(".book-grid");
    const dotsContainer = section.querySelector(".pagination-dots");
    if (!grid || !dotsContainer) return;

    const cards = grid.querySelectorAll(".book-card");
    const cardCount = cards.length;

    dotsContainer.innerHTML = "";
    for (let i = 0; i < cardCount; i++) {
      const dot = document.createElement("div");
      dot.className = "dot" + (i === 0 ? " active" : "");
      dot.addEventListener("click", () => {
        cards[i].scrollIntoView({ behavior: "smooth", inline: "start", block: "nearest" });
      });
      dotsContainer.appendChild(dot);
    }

    grid.addEventListener("scroll", () => {
      const scrollLeft = grid.scrollLeft;
      const cardWidth = cards[0]?.offsetWidth + 12 || 0;
      const activeIndex = Math.round(scrollLeft / cardWidth);
      dotsContainer.querySelectorAll(".dot").forEach((dot, idx) => {
        dot.classList.toggle("active", idx === activeIndex);
      });
    });
  });
});

// ============================================
// LOAD MORE FUNCTIONALITY (Category & Product)
// ============================================
document.addEventListener("DOMContentLoaded", function () {
  // Helper: Create Book/Product Card
  function createBookCard(item, urlPrefix = '/books/') {
    try {
      const card = document.createElement('div');
      card.className = 'book-card';
      
      const link = document.createElement('a');
      link.href = `${urlPrefix}${item.slug}/`;
      link.className = 'book-card-link';
      
      const priceHtml = item.old_price
        ? `<p class="price"><span class="old">Rs. ${item.old_price}</span> Rs. ${item.price}</p>`
        : `<p class="price">Rs. ${item.price}</p>`;
        
      const saleTag = item.on_sale ? `<span class="sale-tag">Sale</span>` : '';

      link.innerHTML = `
        <img src="${item.image_url}" alt="${item.title}" 
             onerror="this.src='/static/images/placeholder.png'; this.onerror=null;" />
        ${saleTag}
        <h3 class="book-title">${item.title}</h3>
        ${priceHtml}
      `;
      
      const btn = document.createElement('button');
      btn.className = 'cart-btn add-to-cart-btn';
      btn.dataset.id = item.id;
      btn.dataset.type = 'book';
      btn.dataset.title = item.title;
      btn.dataset.price = item.price;
      btn.dataset.image = item.image_url;
      btn.textContent = 'Add to cart';
      
      card.appendChild(link);
      card.appendChild(btn);
      
      return card;
    } catch (error) {
      console.error("Error creating card:", error);
      return null;
    }
  }

  // Category Page Load More
  const categoryLoadMoreBtn = document.getElementById("loadMoreBtn");
  const categoryBookGrid = document.getElementById("bookGrid");
  
  if (categoryLoadMoreBtn && categoryBookGrid) {
    console.log("Category Load More: Initializing");
    let currentCategoryPage = 1;
    
    categoryLoadMoreBtn.addEventListener("click", async function () {
      categoryLoadMoreBtn.disabled = true;
      categoryLoadMoreBtn.textContent = "Loading...";
      
      try {
        currentCategoryPage++;
        const categorySlug = categoryBookGrid.dataset.categorySlug;
        
        console.log(`Loading page ${currentCategoryPage} for category: ${categorySlug}`);
        
        const response = await fetch(
          `/category/${categorySlug}/load-more/?page=${currentCategoryPage}`
        );
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        console.log("Category load more response:", data);
        
        if (data.success && data.books && data.books.length > 0) {
          data.books.forEach((book) => {
            const bookCard = createBookCard(book, '/books/');
            if (bookCard) {
              categoryBookGrid.appendChild(bookCard);
              console.log("Appended book card:", book.title);
            }
          });
          
          if (!data.has_next) {
            categoryLoadMoreBtn.style.display = "none";
            console.log("No more books to load");
          }
        } else {
          categoryLoadMoreBtn.style.display = "none";
          console.log("No books returned from server");
        }
      } catch (error) {
        console.error("Category load more error:", error);
        categoryLoadMoreBtn.textContent = "Error - Try Again";
        setTimeout(() => {
          categoryLoadMoreBtn.disabled = false;
          categoryLoadMoreBtn.textContent = "Load More Books";
        }, 3000);
      } finally {
        categoryLoadMoreBtn.disabled = false;
        categoryLoadMoreBtn.textContent = "Load More Books";
      }
    });
  }

  // Product Category Page Load More
  const productLoadMoreBtn = document.getElementById("loadMoreProductsBtn");
  const productGrid = document.getElementById("productGrid");
  
  if (productLoadMoreBtn && productGrid) {
    console.log("Product Load More: Initializing");
    let currentProductPage = 1;
    
    productLoadMoreBtn.addEventListener("click", async function () {
      productLoadMoreBtn.disabled = true;
      productLoadMoreBtn.textContent = "Loading...";
      
      try {
        currentProductPage++;
        const categoryType = productGrid.dataset.categoryType;
        
        console.log(`Loading page ${currentProductPage} for product category: ${categoryType}`);
        
        const response = await fetch(
          `/productcatagory/${categoryType}/load-more/?page=${currentProductPage}`
        );
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const data = await response.json();
        console.log("Product load more response:", data);
        
        if (data.success && data.products && data.products.length > 0) {
          data.products.forEach((product) => {
            const productCard = createBookCard(product, '/product/');
            if (productCard) {
              productGrid.appendChild(productCard);
              console.log("Appended product card:", product.title);
            }
          });
          
          if (!data.has_next) {
            productLoadMoreBtn.style.display = "none";
            console.log("No more products to load");
          }
        } else {
          productLoadMoreBtn.style.display = "none";
          console.log("No products returned from server");
        }
      } catch (error) {
        console.error("Product load more error:", error);
        productLoadMoreBtn.textContent = "Error - Try Again";
        setTimeout(() => {
          productLoadMoreBtn.disabled = false;
          productLoadMoreBtn.textContent = "Load More Products";
        }, 3000);
      } finally {
        productLoadMoreBtn.disabled = false;
        productLoadMoreBtn.textContent = "Load More Products";
      }
    });
  }
  

});