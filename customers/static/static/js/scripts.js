// Update year dynamically
document.getElementById("year").textContent = new Date().getFullYear();

// Open and close sliding menu
function openMenu() {
    const menu = document.getElementById("sideMenu");
    menu.classList.add("open");
}

function closeMenu() {
    const menu = document.getElementById("sideMenu");
    menu.classList.remove("open");
}

// Ensure menu is hidden on page load
document.addEventListener("DOMContentLoaded", () => {
    const menu = document.getElementById("sideMenu");
    menu.classList.remove("open"); // Ensure it is hidden by default
});


// Text Animation for Hero Section
const animatedText = document.getElementById("animated-text");
const messages = ["Mekco Supply", "Plumbing Supply", "Quality You Trust", "Unbeatable Prices"];
let messageIndex = 0;

function updateText() {
    animatedText.textContent = messages[messageIndex];
    messageIndex = (messageIndex + 1) % messages.length;
}

setInterval(updateText, 5000);
updateText();
