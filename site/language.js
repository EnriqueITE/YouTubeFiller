const languageKey = 'youtube-filler.site.language';
for (const link of document.querySelectorAll('[data-lang]')) {
  link.addEventListener('click', () => {
    try { localStorage.setItem(languageKey, link.dataset.lang); } catch {}
  });
}
if (document.documentElement.lang === 'es') {
  let choice;
  try { choice = localStorage.getItem(languageKey); } catch {}
  const languages = navigator.languages?.length ? navigator.languages : [navigator.language];
  const preferred = choice || languages.map(tag => tag.toLowerCase().split('-')[0]).find(lang => lang === 'en' || lang === 'es');
  if (preferred === 'en') location.replace('en/index.html' + location.search + location.hash);
}
