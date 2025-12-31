document.addEventListener('DOMContentLoaded', function(){
  const menuBtn = document.querySelector('.menu-btn');
  const nav = document.querySelector('nav');
  if(!menuBtn || !nav) return;

  menuBtn.addEventListener('click', function(e){
    nav.classList.toggle('open');
  });

  // close menu when clicking a link or outside
  document.addEventListener('click', function(e){
    if(!nav.classList.contains('open')) return;
    const isInside = nav.contains(e.target);
    if(!isInside){
      nav.classList.remove('open');
    }
  });

  // close when any nav link/button is clicked
  nav.addEventListener('click', function(e){
    // don't close nav when interacting with dropdown buttons
    if (e.target.closest('.dropdown-btn')) return;
    if (e.target.tagName.toLowerCase() === 'a' || e.target.closest('.logout-btn') || e.target.closest('.dropdown-content')){
      nav.classList.remove('open');
    }
  });
});

// Dropdown click/touch support (works even if CSS uses :hover)
document.addEventListener('DOMContentLoaded', function(){
  const dropdownBtns = document.querySelectorAll('.dropdown-btn');
  function closeAllDropdowns(){
    document.querySelectorAll('.dropdown.open').forEach(d=>d.classList.remove('open'));
  }

  dropdownBtns.forEach(btn => {
    btn.addEventListener('click', function(e){
      const parent = btn.closest('.dropdown');
      if(!parent) return;
      const isOpen = parent.classList.contains('open');
      closeAllDropdowns();
      if(!isOpen) parent.classList.add('open');
      e.stopPropagation();
    });
  });

  // close dropdowns when clicking outside
  document.addEventListener('click', function(e){
    if(!e.target.closest('.dropdown')){
      closeAllDropdowns();
    }
  });
});