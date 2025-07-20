window.addEventListener('load', () => {
  fetch('/validate-session')  // Verify here because beacon can't redirect
    .then(res => {
      if (res.status === 401) {
        window.location.href = '/login';
      }
    })
    .catch(() => {
      window.location.href = '/login';
    });
});

document.addEventListener("DOMContentLoaded", () => {
  const chevrons = document.querySelectorAll(".passwordContainer__item__header-chevron");

  chevrons.forEach(chevron => {
    chevron.addEventListener("click", () => {
      const item = chevron.closest(".passwordContainer__item");
      const drawer = item.querySelector(".passwordContainer__item__drawer");

      drawer.classList.toggle("collapsed");
      chevron.classList.toggle("rotated");
    });
  });
});


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

window.addEventListener('pagehide', (event) => {
  navigator.sendBeacon('/logout');
});
