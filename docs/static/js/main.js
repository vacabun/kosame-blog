/**
 * Kosame Maid Blog Archive - Main JavaScript
 * Handles search, filtering, lightbox, reading progress, and animations.
 */

document.addEventListener('DOMContentLoaded', () => {
  initReadingProgress();
  initBackToTop();
  initLightbox();
  initSearchAndFilter();
});

/* --------------------------------------------------------------------------
   1. Reading Progress Bar
   -------------------------------------------------------------------------- */
function initReadingProgress() {
  const progressBar = document.getElementById('readProgress');
  if (!progressBar) return;

  window.addEventListener('scroll', () => {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight <= 0) {
      progressBar.style.width = '0%';
      return;
    }
    const progress = (window.pageYOffset / totalHeight) * 100;
    progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;
  }, { passive: true });
}

/* --------------------------------------------------------------------------
   2. Back to Top Button
   -------------------------------------------------------------------------- */
function initBackToTop() {
  const backBtn = document.getElementById('backToTop');
  if (!backBtn) return;

  window.addEventListener('scroll', () => {
    if (window.pageYOffset > 350) {
      backBtn.classList.add('visible');
    } else {
      backBtn.classList.remove('visible');
    }
  }, { passive: true });

  backBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* --------------------------------------------------------------------------
   3. Lightbox Image Viewer
   -------------------------------------------------------------------------- */
function initLightbox() {
  const modal = document.getElementById('lightboxModal');
  if (!modal) return;

  const modalImg = document.getElementById('lightboxImg');
  const caption = document.getElementById('lightboxCaption');
  const closeBtn = document.getElementById('lightboxClose');
  const backdrop = modal.querySelector('.lightbox-backdrop');

  function openLightbox(src, alt) {
    modalImg.src = src;
    caption.textContent = alt || '';
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeLightbox() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
    setTimeout(() => {
      modalImg.src = '';
    }, 200);
  }

  // Attach to article images
  const postBody = document.getElementById('postContent');
  if (postBody) {
    postBody.querySelectorAll('img').forEach(img => {
      img.addEventListener('click', (e) => {
        e.preventDefault();
        openLightbox(img.src, img.alt);
      });
    });
  }

  // Attach to .lightbox-trigger
  document.querySelectorAll('.lightbox-trigger').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const href = trigger.getAttribute('href');
      const img = trigger.querySelector('img');
      openLightbox(href || (img ? img.src : ''), img ? img.alt : '');
    });
  });

  if (closeBtn) closeBtn.addEventListener('click', closeLightbox);
  if (backdrop) backdrop.addEventListener('click', closeLightbox);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeLightbox();
    }
  });
}

/* --------------------------------------------------------------------------
   4. Instant Search & Year Filter & Sort (Index Page)
   -------------------------------------------------------------------------- */
function initSearchAndFilter() {
  const searchInput = document.getElementById('searchInput');
  const searchClear = document.getElementById('searchClear');
  const yearTabs = document.querySelectorAll('.year-tab');
  const postsGrid = document.getElementById('postsGrid');
  const resultsCount = document.getElementById('resultsCount');
  const noResults = document.getElementById('noResults');
  const resetSearchBtn = document.getElementById('resetSearchBtn');
  const sortToggleBtn = document.getElementById('sortToggleBtn');
  const sortLabel = document.getElementById('sortLabel');

  if (!postsGrid) return;

  const cards = Array.from(postsGrid.querySelectorAll('.post-card'));
  let currentYear = 'all';
  let searchQuery = '';
  let isNewestFirst = true;

  function filterCards() {
    let visibleCount = 0;
    const query = searchQuery.trim().toLowerCase();

    cards.forEach(card => {
      const year = card.getAttribute('data-year');
      const title = card.getAttribute('data-title') || '';
      const excerpt = card.getAttribute('data-excerpt') || '';

      const matchesYear = (currentYear === 'all' || year === currentYear);
      const matchesSearch = !query || title.includes(query) || excerpt.includes(query);

      if (matchesYear && matchesSearch) {
        card.style.display = '';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (resultsCount) {
      resultsCount.textContent = `(${visibleCount}件)`;
    }

    if (noResults) {
      noResults.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  function sortCards() {
    cards.sort((a, b) => {
      const idA = parseInt(a.getAttribute('data-id'), 10);
      const idB = parseInt(b.getAttribute('data-id'), 10);
      return isNewestFirst ? (idB - idA) : (idA - idB);
    });

    cards.forEach(card => postsGrid.appendChild(card));
  }

  // Search input handler
  if (searchInput) {
    searchInput.addEventListener('input', (e) => {
      searchQuery = e.target.value;
      if (searchClear) {
        searchClear.style.display = searchQuery ? 'flex' : 'none';
      }
      filterCards();
    });
  }

  // Search clear button
  if (searchClear) {
    searchClear.addEventListener('click', () => {
      searchInput.value = '';
      searchQuery = '';
      searchClear.style.display = 'none';
      searchInput.focus();
      filterCards();
    });
  }

  // Year tabs handler
  yearTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      yearTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentYear = tab.getAttribute('data-year');
      filterCards();
    });
  });

  // Sort toggle handler
  if (sortToggleBtn) {
    sortToggleBtn.addEventListener('click', () => {
      isNewestFirst = !isNewestFirst;
      if (sortLabel) {
        sortLabel.textContent = isNewestFirst ? '新しい順' : '古い順';
      }
      sortCards();
    });
  }

  // Reset button in empty state
  if (resetSearchBtn) {
    resetSearchBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      searchQuery = '';
      if (searchClear) searchClear.style.display = 'none';
      currentYear = 'all';
      yearTabs.forEach(t => {
        if (t.getAttribute('data-year') === 'all') {
          t.classList.add('active');
        } else {
          t.classList.remove('active');
        }
      });
      filterCards();
    });
  }
}
