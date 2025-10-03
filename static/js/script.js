document.addEventListener('DOMContentLoaded', () => {
  AOS.init({ duration: 800, once: true });
  document.getElementById('loader').style.display = 'none';
});

function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  const btn = document.getElementById('darkToggle');
  btn.textContent = document.body.classList.contains('dark-mode') ? '☀️ Light Mode' : '🌙 Dark Mode';
}