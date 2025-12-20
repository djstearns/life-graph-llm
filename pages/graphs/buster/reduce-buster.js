// scripts/reduce-buster.js
const fs = require('fs');
const path = require('path');

/** Helpers */
function parseDateISO(dateStr) {
  return new Date(dateStr + 'T00:00:00Z');
}
function fmtDateISO(d) {
  return d.toISOString().slice(0, 10);
}
function stripHtmlAndWhitespace(html = '') {
  // remove HTML tags, collapse whitespace, remove tabs/newlines
  return html.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
}

/**
 * Reduce raw buster array into simplified object and fill missing weeks.
 * @param {Array} items - Parsed buster.json array
 * @returns {Object} { weeks: [...], labels: [...] }
 */
function reduceBuster(items) {
  const weekMap = new Map();
  const labels = [];

  for (const it of items) {
    if (it.kind === 'week') {
      // date may be in item.date or attrs['data-date']
      const date = it.date || it.attrs?.['data-date'];
      if (!date) continue;

      const anchorDataContent = it.anchorAttrs?.['data-content'] || it.attrs?.['data-content'] || null;
      const rawContent = anchorDataContent || it.content || '';
      const cleaned = stripHtmlAndWhitespace(rawContent);
      const hasContent = Boolean(cleaned);

      const simplified = {
        kind: 'week',
        date,
        title: it.title || null,
        hasContent,
        content: cleaned || '',
        classes: it.attrs?.class || null,
        style: it.attrs?.style || null,
        anchorTitle: it.anchorAttrs?.title || null
      };

      // If multiple entries for same date, prefer one with content
      const existing = weekMap.get(date);
      if (!existing || (simplified.hasContent && !existing.hasContent)) {
        weekMap.set(date, simplified);
      }
    } else if (it.kind === 'label') {
      labels.push({ kind: 'label', text: it.text || null, date: it.date || null });
    }
  }

  // If no weeks, return labels-only result
  const weekDates = Array.from(weekMap.keys()).sort();
  if (weekDates.length === 0) return { weeks: [], labels };

  // Fill missing weekly dates (every 7 days) between min and max
  const minDate = parseDateISO(weekDates[0]);
  const maxDate = parseDateISO(weekDates[weekDates.length - 1]);

  const weeks = [];
  for (let cur = new Date(minDate); cur <= maxDate; cur.setUTCDate(cur.getUTCDate() + 7)) {
    const dStr = fmtDateISO(cur);
    const existing = weekMap.get(dStr);
    if (existing) weeks.push(existing);
    else weeks.push({
      kind: 'week',
      date: dStr,
      title: null,
      hasContent: false,
      content: '',
      classes: null,
      style: null,
      anchorTitle: null
    });
  }

  return { weeks, labels };
}

/** CLI usage */
if (require.main === module) {
  const inputPath = process.argv[2] || path.join('docker_app', 'buster.json');
  const outputPath = process.argv[3] || path.join('docker_app', 'buster.simplified.json');

  try {
    const raw = fs.readFileSync(inputPath, 'utf8');
    const items = JSON.parse(raw);
    const reduced = reduceBuster(items);
    fs.writeFileSync(outputPath, JSON.stringify(reduced, null, 2), 'utf8');
    console.log(`Wrote simplified buster: ${outputPath}`);
  } catch (err) {
    console.error('Error:', err.message);
    process.exit(1);
  }
}

module.exports = { reduceBuster };