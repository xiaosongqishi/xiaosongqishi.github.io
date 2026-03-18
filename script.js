(() => {
  'use strict';

  /* ==========================================================
     Dark Mode Toggle — respects system preference & persists
     ========================================================== */
  const themeToggle = document.getElementById('themeToggle');
  const root = document.documentElement;

  function getPreferredTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }

  applyTheme(getPreferredTheme());

  themeToggle.addEventListener('click', () => {
    const current = root.getAttribute('data-theme');
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });

  /* ==========================================================
     Mobile Navigation
     ========================================================== */
  const hamburger = document.getElementById('navHamburger');
  const navLinks = document.getElementById('navLinks');

  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('open');
  });

  navLinks.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('active');
      navLinks.classList.remove('open');
    });
  });

  /* ==========================================================
     Scroll Animations — IntersectionObserver
     ========================================================== */
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.12,
      rootMargin: '0px 0px -40px 0px'
    });

    animatedElements.forEach(el => observer.observe(el));
  } else {
    animatedElements.forEach(el => el.classList.add('visible'));
  }

  /* ==========================================================
     Active Nav Link Highlight on Scroll
     ========================================================== */
  const sections = document.querySelectorAll('section[id], footer[id]');
  const navItems = document.querySelectorAll('.nav-link');

  function highlightNav() {
    const scrollY = window.scrollY + 100;

    sections.forEach(section => {
      const top = section.offsetTop - 100;
      const bottom = top + section.offsetHeight;
      const id = section.getAttribute('id');

      navItems.forEach(link => {
        if (link.getAttribute('href') === '#' + id) {
          if (scrollY >= top && scrollY < bottom) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        }
      });
    });
  }

  let scrollTicking = false;
  window.addEventListener('scroll', () => {
    if (!scrollTicking) {
      requestAnimationFrame(() => {
        highlightNav();
        scrollTicking = false;
      });
      scrollTicking = true;
    }
  });

  highlightNav();

  /* ==========================================================
     Newsletter — load posts from posts-data.json
     ========================================================== */
  const grid = document.getElementById('newsletterGrid');

  if (grid) {
    fetch('posts/posts-data.json')
      .then(res => {
        if (!res.ok) throw new Error(res.status);
        return res.json();
      })
      .then(posts => {
        if (!posts.length) return;
        grid.innerHTML = '';
        posts.forEach((post, i) => {
          const tags = (post.tags || [])
            .map(t => `<span>${t}</span>`)
            .join('');

          const card = document.createElement('a');
          card.href = post.url;
          card.className = 'newsletter-card animate-on-scroll';
          card.style.transitionDelay = `${i * 0.08}s`;
          card.innerHTML = `
            <span class="newsletter-card-date">${post.date}</span>
            <h3 class="newsletter-card-title">${post.title}</h3>
            <p class="newsletter-card-summary">${post.summary}</p>
            <div class="newsletter-card-tags">${tags}</div>
          `;
          grid.appendChild(card);

          if ('IntersectionObserver' in window) {
            const obs = new IntersectionObserver((entries) => {
              entries.forEach(entry => {
                if (entry.isIntersecting) {
                  entry.target.classList.add('visible');
                  obs.unobserve(entry.target);
                }
              });
            }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
            obs.observe(card);
          } else {
            card.classList.add('visible');
          }
        });
      })
      .catch(() => {
        /* posts-data.json not found yet — keep the "no posts" message */
      });
  }
})();
