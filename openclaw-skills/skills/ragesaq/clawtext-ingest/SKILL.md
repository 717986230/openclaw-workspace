---
name: ClawText Ingest
description: Multi-source memory ingestion with automatic deduplication and YAML headers
---

# ClawText Ingest — Skill Definition

**Name:** clawtext-ingest  
**Version:** 1.2.0  
**Author:** ragesaq  
**License:** MIT  
**Category:** Memory & Knowledge Management  

## Overview

ClawText Ingest is a lightweight multi-source data ingestion tool for OpenClaw agents. Convert files, URLs, JSON exports, and raw text into structured memory files with automatic YAML frontmatter, deduplication, and cluster integration.

**Perfect for:** Agents that need to import external knowledge (docs, chat exports, API responses) into the OpenClaw memory system.

## Quick Start

```bash
npm install clawtext-ingest
```

```javascript
import ClawTextIngest from 'clawtext-ingest';

const ingest = new ClawTextIngest();

// Ingest markdown docs
await ingest.fromFiles(['docs/**/*.md'], { project: 'docs', type: 'fact' });

// Ingest Discord/Slack chat export
await ingest.fromJSON(chatArray, { project: 'team' }, {
  keyMap: { contentKey: 'message', dateKey: 'timestamp', authorKey: 'user' }
});

// Run batch and rebuild clusters
const result = await ingest.ingestAll([...sources]);
console.log(`Imported: ${result.totalImported}, Skipped: ${result.totalSkipped}`);
```

## Features

- ✅ **Multi-source ingestion** — Files (glob), URLs, JSON, raw text
- ✅ **Automatic YAML headers** — Date, project, type, entities, keywords
- ✅ **SHA1 deduplication** — Zero duplicates even with repeated ingestion
- ✅ **Batch processing** — Handle 1000s of items efficiently
- ✅ **Entity extraction** — Auto-detect and index entities
- ✅ **Cluster integration** — Works with ClawText RAG layer
- ✅ **Flexible dedup control** — `checkDedupe: true/false` per call

## API

### Constructor
```javascript
new ClawTextIngest(memoryDir, hashFile)
```
- `memoryDir` (string): Path to memory directory (~/.openclaw/workspace/memory)
- `hashFile` (string): Path to hash store (.ingest_hashes.json)

### Methods

**fromFiles(patterns, metadata, options)**
- `patterns`: Glob pattern(s) — `['docs/**/*.md']`
- `metadata`: Common metadata — `{ project: 'docs', type: 'fact' }`
- `options`: `{ checkDedupe: true }`
- Returns: `{ imported, skipped, errors }`

**fromJSON(data, metadata, options)**
- `data`: Array or single object
- `metadata`: Common metadata
- `options`: `{ keyMap, transform, checkDedupe: true }`
  - `keyMap`: Field mapping — `{ contentKey: 'message', dateKey: 'timestamp', authorKey: 'user' }`
  - `transform`: Async function to modify content
- Returns: `{ imported, skipped, errors }`

**fromText(text, metadata)**
- `text`: Raw content string
- `metadata`: Common metadata
- Returns: `{ imported, skipped, errors }`

**ingestAll(sources)**
- `sources`: Array of `{ type, data, metadata }` objects
- Returns: `{ totalImported, totalSkipped, results, errors }`

**commit()**
- Persist hashes to disk
- Returns: Full report

## Requirements

**Peer Dependency:**
- **ClawText RAG Layer** — Provides cluster management and memory injection
  - GitHub: https://github.com/ragesaq/clawtext
  - Required for: Automatic cluster indexing after ingestion

## Integration with ClawText

After ingesting data:

```bash
# 1. Ingest sources
node ingest.mjs

# 2. Rebuild ClawText clusters to index new memories
cd ~/.openclaw/workspace/skills/clawtext
node scripts/build-clusters.js --force

# 3. Validate RAG quality (optional)
node scripts/validate-rag.js
```

New memories are automatically indexed and available for RAG injection on next prompt.

## Examples

### Ingest Markdown Documentation
```javascript
const ingest = new ClawTextIngest();
await ingest.fromFiles(
  ['docs/**/*.md'],
  { project: 'documentation', type: 'fact' }
);
await ingest.commit();
```

### Ingest Discord Chat Export
```javascript
const chatExport = JSON.parse(fs.readFileSync('discord-export.json'));
await ingest.fromJSON(
  chatExport,
  { project: 'team', type: 'decision' },
  {
    keyMap: {
      contentKey: 'content',
      dateKey: 'timestamp',
      authorKey: 'author'
    }
  }
);
```

### Batch Multiple Sources
```javascript
const result = await ingest.ingestAll([
  {
    type: 'files',
    data: ['docs/**/*.md'],
    metadata: { project: 'docs', type: 'fact' }
  },
  {
    type: 'json',
    data: chatExport,
    metadata: { project: 'team', type: 'decision' },
    options: { keyMap: {...} }
  },
  {
    type: 'text',
    data: 'Raw knowledge to import',
    metadata: { project: 'notes', type: 'learning' }
  }
]);
console.log(result); // { totalImported: X, totalSkipped: Y, ... }
```

### Safe Daily Ingestion (No Duplicates)
```javascript
// Run this daily — deduplication prevents duplicates
async function dailyMemorySync() {
  const ingest = new ClawTextIngest();
  const result = await ingest.ingestAll([
    {
      type: 'files',
      data: ['recent-notes/**/*.md'],
      metadata: { project: 'daily' }
    }
  ]);
  return result;
}
```

## Testing

```bash
npm test                    # Basic functionality tests
node test-idempotency.mjs   # Verify deduplication + idempotency
```

## Common Patterns

### Recurring Agent Tasks
Agents can safely call ingest repeatedly without worrying about duplicates:

```javascript
// This runs every hour in a cron job — duplicates are auto-skipped
await ingest.fromFiles(['monitoring/**/*.log'], { project: 'ops' });
```

### Data Transformation
Custom transform function for data processing:

```javascript
await ingest.fromJSON(data, metadata, {
  transform: async (item, content) => {
    // Custom processing
    return processedContent;
  }
});
```

### Dedup Control
Disable checking for maximum performance (use only if you're sure no duplicates exist):

```javascript
await ingest.fromFiles(patterns, metadata, { checkDedupe: false });
```

## Troubleshooting

### "No memories returned after ingest"
- Verify clusters were rebuilt: `node build-clusters.js --force`
- Check ingestion report for skipped/errored items

### "High memory usage on large files"
- Use batch processing with smaller `maxItems` per batch
- Process files sequentially rather than in parallel

### "Deduplication seems slow"
- Normal for first run (building hash index)
- Subsequent runs are fast (hash lookup is O(1))
- Can disable with `checkDedupe: false` if needed

## Performance

- **Ingestion speed:** ~5,000 items/minute (depends on file size, network)
- **Deduplication:** O(1) hash lookup, negligible overhead
- **Memory:** ~1MB per 1000 hashes stored
- **Cluster rebuild:** Automatic, triggered by ClawText on next load

## License

MIT

## See Also

- **ClawText RAG** — https://github.com/ragesaq/clawtext (peer dependency)
- **OpenClaw** — https://github.com/openclaw/openclaw
- **ClawhHub** — https://clawhub.com (skill discovery)

---

**Version:** 1.2.0  
**Updated:** 2026-03-03  
**Author:** ragesaq  
**Repository:** https://github.com/ragesaq/clawtext-ingest
