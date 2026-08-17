/* Dropdown navigation: hover on desktop, tap on touch devices. */
(function () {
  var items = document.querySelectorAll('.nav-item');
  if (!items.length) return;

  function closeAll(except) {
    items.forEach(function (it) {
      if (it !== except) {
        it.classList.remove('open');
        var t = it.querySelector('.nav-parent');
        if (t) t.setAttribute('aria-expanded', 'false');
      }
    });
  }

  items.forEach(function (item) {
    var parent = item.querySelector('.nav-parent');
    if (!parent) return;

    parent.addEventListener('click', function (e) {
      e.preventDefault();
      var isOpen = item.classList.contains('open');
      closeAll(item);
      item.classList.toggle('open', !isOpen);
      parent.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
    });

    parent.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') { closeAll(); parent.blur(); }
    });
  });

  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav-item')) closeAll();
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeAll();
  });
})();
