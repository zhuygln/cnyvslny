export interface Entry {
  entity_name: string;
  entity_type: 'company' | 'school' | 'gov' | 'media' | 'nonprofit' | 'app' | 'other';
  country_or_region: string;
  term_used: string | string[];
  exact_phrase: string;
  context: 'social_post' | 'press_release' | 'product_ui' | 'email' | 'event_page' | 'website' | 'other';
  platform: string;
  sources: { url: string; evidence?: string }[];
  captured_on: string;
  contributor: string;
  notes?: string;
}

export type Column = 'cny' | 'lny';

export function classifyEntry(entry: Entry): Column | 'both' {
  const terms = Array.isArray(entry.term_used) ? entry.term_used : [entry.term_used];
  const hasChinese = terms.some(t => /chinese/i.test(t));
  const hasLunar = terms.some(t => /lunar/i.test(t));
  if (hasChinese && hasLunar) return 'both';
  if (hasLunar) return 'lny';
  return 'cny';
}
