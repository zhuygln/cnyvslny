import fs from 'node:fs';
import path from 'node:path';
import type { Entry } from '../types/entry';

export function loadEntries(): Entry[] {
  const dataDir = path.resolve(import.meta.dirname, '../../../data');
  const files = fs.readdirSync(dataDir).filter((f) => f.endsWith('.jsonl')).sort().reverse();

  const entries: Entry[] = [];

  for (const file of files) {
    const content = fs.readFileSync(path.join(dataDir, file), 'utf-8');
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (trimmed) {
        entries.push(JSON.parse(trimmed) as Entry);
      }
    }
  }

  // Sort newest first by captured_on
  entries.sort((a, b) => b.captured_on.localeCompare(a.captured_on));

  return entries;
}
