console.log("Token:", window.AUTH_TOKEN);

function setView(category, clickedElement) {
  const items = document.querySelectorAll('.content-item');
  
  items.forEach(item => {
    if (category === 'all' || item.getAttribute('data-category') === category) {
      item.classList.remove('hidden');
    } else {
      item.classList.add('hidden');
    }
  });
document.querySelectorAll('.sidebar__section__item').forEach(item => {
    item.classList.remove('active');
  });

  // Add 'active' to the clicked one
  clickedElement.classList.add('active');
}
