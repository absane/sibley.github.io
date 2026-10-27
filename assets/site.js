// All content and navigation work without JavaScript.
document.querySelectorAll('[data-year]').forEach((element) => {
  element.textContent = new Date().getFullYear();
});
document.querySelector('[data-print]')?.addEventListener('click', () => window.print());
