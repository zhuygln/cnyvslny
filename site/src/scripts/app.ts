interface Entry {
  entity_name: string;
  entity_type: string;
  country_or_region: string;
  term_used: string;
  exact_phrase: string;
  context: string;
  platform: string;
  source_url: string;
  captured_on: string;
  contributor: string;
  notes?: string;
}

type Column = 'cny' | 'lny';

declare global {
  interface Window {
    __CNYVSLNY_DATA__: Entry[];
  }
}

const PAGE_SIZE = 20;

function classifyEntry(entry: Entry): Column {
  return entry.term_used === 'Lunar New Year' ? 'lny' : 'cny';
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

const ENTITY_TYPE_CLASSES: Record<string, Record<Column, string>> = {
  company: { cny: 'bg-red-900/60 text-yellow-200', lny: 'bg-blue-900/60 text-blue-200' },
  school: { cny: 'bg-red-900/60 text-yellow-200', lny: 'bg-blue-900/60 text-blue-200' },
  gov: { cny: 'bg-red-900/60 text-yellow-200', lny: 'bg-blue-900/60 text-blue-200' },
  media: { cny: 'bg-red-900/60 text-yellow-200', lny: 'bg-blue-900/60 text-blue-200' },
  nonprofit: { cny: 'bg-red-900/60 text-yellow-200', lny: 'bg-blue-900/60 text-blue-200' },
  app: { cny: 'bg-red-900/60 text-yellow-200', lny: 'bg-blue-900/60 text-blue-200' },
  other: { cny: 'bg-red-900/60 text-yellow-300/70', lny: 'bg-blue-900/60 text-blue-300/70' },
};

const CONTEXT_LABELS: Record<string, string> = {
  social_post: 'Social Post',
  press_release: 'Press Release',
  product_ui: 'Product UI',
  email: 'Email',
  event_page: 'Event Page',
  website: 'Website',
  other: 'Other',
};

function renderCard(entry: Entry, column: Column): string {
  const typeEntry = ENTITY_TYPE_CLASSES[entry.entity_type];
  const fallback = column === 'lny' ? 'bg-blue-900/60 text-blue-300/70' : 'bg-red-900/60 text-yellow-300/70';
  const typeClasses = typeEntry ? typeEntry[column] : fallback;
  const contextLabel = CONTEXT_LABELS[entry.context] || entry.context;

  if (column === 'lny') {
    return `<div class="p-4 hover:bg-blue-700/50 transition-all duration-200 ease-in-out hover:-translate-y-[2px]">
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <h3 class="font-medium text-sm truncate text-blue-100">${escapeHtml(entry.entity_name)}</h3>
        <p class="text-xs text-blue-300/70 mt-0.5">${escapeHtml(entry.country_or_region)}</p>
      </div>
      <span class="shrink-0 text-xs font-medium rounded-full px-2 py-0.5 ${typeClasses}">${escapeHtml(entry.entity_type)}</span>
    </div>
    <p class="mt-2 text-sm italic text-blue-100">"${escapeHtml(entry.exact_phrase)}"</p>
    <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-blue-300/60">
      <span>${escapeHtml(contextLabel)}</span>
      <span>· ${escapeHtml(entry.platform)}</span>
      <span>· ${escapeHtml(entry.captured_on)}</span>
    </div>
    ${entry.notes ? `<p class="mt-1.5 text-xs text-blue-400/50">${escapeHtml(entry.notes)}</p>` : ''}
    <a href="${escapeHtml(entry.source_url)}" target="_blank" rel="noopener noreferrer" class="mt-2 inline-block text-xs text-blue-200 hover:text-blue-100 hover:underline transition-colors duration-200">Source ↗</a>
  </div>`;
  }

  return `<div class="p-4 hover:bg-red-700/50 transition-all duration-200 ease-in-out hover:-translate-y-[2px]">
    <div class="flex items-start justify-between gap-2">
      <div class="min-w-0">
        <h3 class="font-medium text-sm truncate text-yellow-200">${escapeHtml(entry.entity_name)}</h3>
        <p class="text-xs text-yellow-400/70 mt-0.5">${escapeHtml(entry.country_or_region)}</p>
      </div>
      <span class="shrink-0 text-xs font-medium rounded-full px-2 py-0.5 ${typeClasses}">${escapeHtml(entry.entity_type)}</span>
    </div>
    <p class="mt-2 text-sm italic text-yellow-100">"${escapeHtml(entry.exact_phrase)}"</p>
    <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-yellow-400/60">
      <span>${escapeHtml(contextLabel)}</span>
      <span>· ${escapeHtml(entry.platform)}</span>
      <span>· ${escapeHtml(entry.captured_on)}</span>
    </div>
    ${entry.notes ? `<p class="mt-1.5 text-xs text-yellow-500/50">${escapeHtml(entry.notes)}</p>` : ''}
    <a href="${escapeHtml(entry.source_url)}" target="_blank" rel="noopener noreferrer" class="mt-2 inline-block text-xs text-yellow-300 hover:text-yellow-100 hover:underline transition-colors duration-200">Source ↗</a>
  </div>`;
}

function init() {
  const allEntries: Entry[] = window.__CNYVSLNY_DATA__ || [];
  const searchInput = document.getElementById('search-input') as HTMLInputElement;
  const cnyCards = document.getElementById('cny-cards')!;
  const lnyCards = document.getElementById('lny-cards')!;
  const cnySentinel = document.getElementById('cny-sentinel')!;
  const lnySentinel = document.getElementById('lny-sentinel')!;
  const cnyCount = document.getElementById('cny-count')!;
  const lnyCount = document.getElementById('lny-count')!;
  const cnyColumn = document.getElementById('cny-column')!;
  const lnyColumn = document.getElementById('lny-column')!;

  let cnyFiltered: Entry[] = [];
  let lnyFiltered: Entry[] = [];
  let cnyPage = 0;
  let lnyPage = 0;
  let cnyObserver: IntersectionObserver | null = null;
  let lnyObserver: IntersectionObserver | null = null;

  function filterEntries(query: string) {
    const q = query.toLowerCase();
    const filtered = q
      ? allEntries.filter((e) =>
          e.entity_name.toLowerCase().includes(q) ||
          e.exact_phrase.toLowerCase().includes(q) ||
          e.platform.toLowerCase().includes(q) ||
          (e.notes && e.notes.toLowerCase().includes(q))
        )
      : allEntries;

    cnyFiltered = [];
    lnyFiltered = [];
    for (const entry of filtered) {
      if (classifyEntry(entry) === 'cny') {
        cnyFiltered.push(entry);
      } else {
        lnyFiltered.push(entry);
      }
    }
  }

  function renderPage(column: Column) {
    const entries = column === 'cny' ? cnyFiltered : lnyFiltered;
    const page = column === 'cny' ? cnyPage : lnyPage;
    const container = column === 'cny' ? cnyCards : lnyCards;
    const start = page * PAGE_SIZE;
    const end = Math.min(start + PAGE_SIZE, entries.length);

    if (start >= entries.length) return;

    const fragment = document.createDocumentFragment();
    for (let i = start; i < end; i++) {
      const wrapper = document.createElement('div');
      wrapper.innerHTML = renderCard(entries[i], column);
      fragment.appendChild(wrapper.firstElementChild!);
    }
    container.appendChild(fragment);

    if (column === 'cny') {
      cnyPage++;
    } else {
      lnyPage++;
    }
  }

  function hasMore(column: Column): boolean {
    const entries = column === 'cny' ? cnyFiltered : lnyFiltered;
    const page = column === 'cny' ? cnyPage : lnyPage;
    return page * PAGE_SIZE < entries.length;
  }

  function setupObserver(column: Column) {
    const sentinel = column === 'cny' ? cnySentinel : lnySentinel;
    const scrollContainer = column === 'cny' ? cnyColumn : lnyColumn;
    const isDesktop = window.matchMedia('(min-width: 768px)').matches;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore(column)) {
          renderPage(column);
          if (!hasMore(column)) {
            observer.disconnect();
          }
        }
      },
      {
        root: isDesktop ? scrollContainer : null,
        rootMargin: '200px',
      }
    );

    observer.observe(sentinel);
    return observer;
  }

  function reset() {
    cnyCards.innerHTML = '';
    lnyCards.innerHTML = '';
    cnyPage = 0;
    lnyPage = 0;

    if (cnyObserver) cnyObserver.disconnect();
    if (lnyObserver) lnyObserver.disconnect();

    cnyCount.textContent = String(cnyFiltered.length);
    lnyCount.textContent = String(lnyFiltered.length);

    renderPage('cny');
    renderPage('lny');

    cnyObserver = setupObserver('cny');
    lnyObserver = setupObserver('lny');
  }

  // Debounced search
  let debounceTimer: ReturnType<typeof setTimeout>;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      filterEntries(searchInput.value.trim());
      reset();
    }, 200);
  });

  // Initial render
  filterEntries('');
  reset();
}

document.addEventListener('DOMContentLoaded', init);
