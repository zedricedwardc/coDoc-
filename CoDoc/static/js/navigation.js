document.addEventListener("DOMContentLoaded", () => {
  // Burger menu elements
  const burgerBtn = document.getElementById("burger-btn")
  const menuDropdown = document.getElementById("menu-dropdown")
  const menuItems = document.querySelectorAll(".menu-item")

  // Toggle burger menu
  burgerBtn.addEventListener("click", (e) => {
    e.stopPropagation()
    menuDropdown.classList.toggle("hidden")
  })

  // Close menu when clicking outside
  document.addEventListener("click", (event) => {
    if (!burgerBtn.contains(event.target) && !menuDropdown.contains(event.target)) {
      menuDropdown.classList.add("hidden")
    }
  })

  // Set active menu item based on current page
  const currentPath = window.location.pathname
  menuItems.forEach((item) => {
    const href = item.getAttribute("href")
    if (href === currentPath || (currentPath === "/" && href.includes("analyzer"))) {
      item.classList.add("active")
    } else {
      item.classList.remove("active")
    }
  })
})
