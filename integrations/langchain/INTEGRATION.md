# LangChain Integration for OpenClaw

## Overview

This integration provides seamless connection between OpenClaw and the LangChain framework, enabling advanced chain orchestration, tool composition, and memory management capabilities.

## Architecture

```
integrations/langchain/
├── INTEGRATION.md          # This file
├── tools/                  # Tool wrappers
│   ├── index.ts           # Tool registry
│   ├── openclaw-tool.ts   # Base OpenClaw tool wrapper
│   └── tool-adapter.ts    # LangChain tool adapter
├── chains/                 # Chain management
│   ├── index.ts           # Chain registry
│   ├── chain-manager.ts   # Chain execution manager
│   └── chain-builder.ts   # Chain builder utilities
├── memory/                # Memory integration
│   ├── index.ts           # Memory registry
│   ├── openclaw-memory.ts # OpenClaw memory adapter
│   └── context-manager.ts # Context management
├── examples/              # Example usage
│   ├── basic-chain.ts     # Basic chain example
│   ├── tool-chain.ts      # Tool chain example
│   └── memory-chain.ts    # Memory chain example
└── tests/                 # Test files
    ├── tools.test.ts      # Tool tests
    ├── chains.test.ts     # Chain tests
    └── memory.test.ts     # Memory tests
```

## Integration Points

### 1. Tool Chain Management

OpenClaw tools can be wrapped as LangChain tools:

```typescript
import { OpenClawTool } from './tools/openclaw-tool';
import { ToolChainManager } from './chains/chain-manager';

// Wrap OpenClaw tools
const tools = [
  new OpenClawTool('web_search', webSearchTool),
  new OpenClawTool('file_reader', fileReaderTool),
];

// Create chain manager
const chainManager = new ToolChainManager(tools);
```

### 2. Chain Execution

Chains can be executed with proper context flow:

```typescript
import { ChainBuilder } from './chains/chain-builder';

const chain = new ChainBuilder()
  .addStep('search', webSearchTool)
  .addStep('summarize', summarizeTool)
  .addStep('store', memoryStoreTool)
  .build();

const result = await chain.execute({ query: 'latest AI news' });
```

### 3. Memory System Integration

OpenClaw memory system integrates with LangChain's memory primitives:

```typescript
import { OpenClawMemory } from './memory/openclaw-memory';

const memory = new OpenClawMemory({
  sessionId: 'user-session-123',
  maxTokens: 4000,
});

// Use in conversation chain
const chain = new ConversationChain({
  llm: llm,
  memory: memory,
});
```

### 4. Context Management

Context flows through chains with proper isolation:

```typescript
import { ContextManager } from './memory/context-manager';

const contextManager = new ContextManager();
const context = contextManager.createContext({
  userId: 'user-123',
  sessionId: 'session-456',
});

// Context automatically propagates through chain execution
```

## Key Features

### Tool Wrapping
- Automatic conversion of OpenClaw tools to LangChain format
- Preserves tool metadata and schemas
- Handles async execution and error states

### Chain Orchestration
- Sequential chain execution
- Parallel tool execution support
- Conditional branching in chains
- Error recovery and retry logic

### Memory Integration
- Session-based memory isolation
- Short-term and long-term memory mapping
- Automatic context window management
- Memory pruning and summarization

### Context Propagation
- Request-scoped context
- User identity propagation
- Session tracking
- Audit trail support

## Configuration

### Environment Variables

```bash
LANGCHAIN_TRACING=true
LANGCHAIN_API_KEY=your_api_key
OPENCLAW_SESSION_TIMEOUT=3600
OPENCLAW_MAX_CONTEXT_TOKENS=8000
```

### Integration Config

```typescript
interface LangChainIntegrationConfig {
  enabled: boolean;
  tracing: boolean;
  memory: {
    backend: 'openclaw' | 'redis' | 'memory';
    maxSessionAge: number;
  };
  chains: {
    maxConcurrency: number;
    timeout: number;
    retryAttempts: number;
  };
}
```

## Usage Examples

### Basic Tool Chain

```typescript
import { createToolChain } from './tools';

const chain = createToolChain([
  { name: 'search', tool: webSearch },
  { name: 'extract', tool: contentExtractor },
  { name: 'analyze', tool: analyzer },
]);

const result = await chain.run('Analyze recent tech news');
```

### Memory-Enabled Conversation

```typescript
import { createMemoryChain } from './memory';

const chain = createMemoryChain({
  tools: [calculator, webSearch],
  memory: 'persistent',
  sessionId: 'user-123',
});

const response = await chain.chat('What is the weather?');
```

### Parallel Execution

```typescript
import { ChainBuilder } from './chains';

const chain = new ChainBuilder()
  .parallel([
    { name: 'search1', tool: searchEngine1 },
    { name: 'search2', tool: searchEngine2 },
  ])
  .merge(mergeResults)
  .addStep('synthesize', synthesizer)
  .build();

await chain.execute({ query: 'multi-source search' });
```

## Best Practices

1. **Tool Design**: Keep tools single-purpose and well-documented
2. **Chain Length**: Prefer shorter chains with clear steps
3. **Memory Usage**: Clear old sessions regularly
4. **Error Handling**: Always handle tool failures gracefully
5. **Context Size**: Monitor token usage to avoid context overflow

## Dependencies

```json
{
  "dependencies": {
    "langchain": "^0.1.0",
    "@langchain/core": "^0.1.0",
    "@langchain/community": "^0.0.20"
  }
}
```

## Testing

Run tests with:

```bash
npm run test:integration:langchain
```

## Troubleshooting

### Common Issues

1. **Context Overflow**: Reduce chain complexity or increase max tokens
2. **Tool Timeout**: Adjust timeout in chain configuration
3. **Memory Leak**: Ensure proper session cleanup
4. **Chain Execution Error**: Check tool input schemas

## Contributing

When adding new tools or chains:
1. Follow the established patterns in existing implementations
2. Add comprehensive tests
3. Update this documentation
4. Ensure backward compatibility

## Version History

- v1.0.0 - Initial integration with basic tool and memory support
- v1.1.0 - Added chain builder and context management
- v1.2.0 - Added parallel execution and error recovery
