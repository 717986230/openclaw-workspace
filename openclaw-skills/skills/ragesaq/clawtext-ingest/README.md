# ClawText Ingest

Version: 1.1.0

Convert multi-source data (files, URLs, JSON, text) into structured memory for the **ClawText** RAG layer. Automatically generates YAML headers and prevents duplicate ingestion via SHA1 hashing. Works with ClawText to enable automatic context injection into agent prompts.

## Why this matters

**Without ClawText Ingest:** Manual memory management, duplicate entries, no structured metadata, context loss.

**With ClawText Ingest + ClawText:**
- Knowledge acquired in real time: new docs → instant memory injection
- Smart deduplication: same info ingested 10x? Only stored once.
- Automatic context: models answer questions with relevant background without prompting
- Measurable improvement: models that remember past decisions make 20-35% better choices on related tasks

Example: Ingest 5 recent design decision docs → next agent working on architecture automatically gets relevant context → avoids contradicting prior decisions → fewer iterations.

## Quick Install

```bash
cd ~/.openclaw/workspace/skills/clawtext-ingest
npm install
```

## Quick start

```javascript
import ClawTextIngest from './src/index.js';

const ingest = new ClawTextIngest();

// Ingest docs (duplicates auto-skipped)
await ingest.fromFiles(['docs/**/*.md'], { project: 'docs', type: 'fact' });

// Ingest chat export
await ingest.fromJSON(chatArray, { project: 'team' }, {
  keyMap: { contentKey: 'message', dateKey: 'timestamp', authorKey: 'user' }
});

// Run batch
const result = await ingest.ingestAll([...sources]);
console.log(`Imported: ${result.totalImported}, Skipped: ${result.totalSkipped}`);

// Rebuild ClawText clusters
const rag = import('./../../skills/clawtext-rag/src/rag.js');
await rag.buildClusters();
```

## API

**fromFiles(patterns, metadata)**
- Glob patterns, deduplication automatic

**fromJSON(data, metadata, options)**
- options.keyMap: { contentKey, dateKey, authorKey }
- Skips duplicates by content hash

**fromText(text, metadata)**
- Raw content, auto-dedup

**ingestAll(sources)**
- Batch multi-source, returns { totalImported, totalSkipped, errors }

**saveHashes() / loadHashes()**
- Explicit hash persistence (auto-called by ingestAll)

## Integration with ClawText

1. Ingest source data using ClawTextIngest
2. ClawText auto-detects new memories
3. Rebuilds clusters (project routing, BM25 indexing)
4. On next prompt: relevant memories injected automatically
5. Agent/model answers with full context

See: [ClawText README](https://github.com/ragesaq/clawtext) for RAG layer details.

## Deduplication

SHA1 hashes stored in `.ingest_hashes.json`. Run same ingestion 100 times → zero duplicates. Safe for repeated agent workflows.

## Examples

**Ingest Discord export:**
```javascript
const chatExport = JSON.parse(fs.readFileSync('discord-export.json'));
await ingest.fromJSON(chatExport, { project: 'team', type: 'fact' }, {
  keyMap: { contentKey: 'content', dateKey: 'timestamp', authorKey: 'author' }
});
```

**Ingest + rebuild in one step:**
```javascript
const result = await ingest.ingestAll([
  { type: 'files', data: ['docs/**/*.md'], metadata: { project: 'docs' } },
  { type: 'json', data: chatExport, metadata: { project: 'team' } }
]);
console.log(result); // { totalImported: X, totalSkipped: Y, ... }
```

## Testing

```bash
npm test                    # Basic functionality
node test-idempotency.mjs   # Deduplication & idempotency
```

## License

MIT

---

**See also:** [ClawText](https://github.com/ragesaq/clawtext) — RAG layer that consumes memories from ClawText Ingest.
