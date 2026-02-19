export interface Entry {
  entity_name: string;
  entity_type: 'company' | 'school' | 'gov' | 'media' | 'nonprofit' | 'app' | 'other';
  country_or_region: string;
  term_used: 'Chinese New Year' | 'Lunar New Year' | 'Lunar New Year (Chinese New Year)' | 'Spring Festival' | 'other';
  exact_phrase: string;
  context: 'social_post' | 'press_release' | 'product_ui' | 'email' | 'event_page' | 'website' | 'other';
  platform: string;
  source_url: string;
  captured_on: string;
  contributor: string;
  notes?: string;
  evidence?: string;
}

export type Column = 'cny' | 'lny';

export function classifyEntry(entry: Entry): Column {
  return entry.term_used === 'Lunar New Year' ? 'lny' : 'cny';
}
