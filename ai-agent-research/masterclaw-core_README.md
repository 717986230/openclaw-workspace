# MasterClaw Core 🧠

The AI brain — LLM integrations, memory systems, agent orchestration, and tool handlers.

## 📇 Master Index

**[INDEX.md](./INDEX.md)** — Master navigation for the entire MasterClaw ecosystem

## Project Links 📎

- [WHATSNEW.md](./WHATSNEW.md) — Latest features and improvements
- [LICENSE](./LICENSE) — MIT License
- [CONTRIBUTING](./CONTRIBUTING.md) — How to contribute
- [CODE_OF_CONDUCT](./CODE_OF_CONDUCT.md) — Community standards
- [ROADMAP](./ROADMAP.md) — Future development plans
- [Makefile](./Makefile) — Cross-repo orchestration (run `make help`)
- [CHEATSHEET.md](./CHEATSHEET.md) — Quick reference for mc commands
- [Issue Templates](./.github/ISSUE_TEMPLATE/) — Bug reports, features, questions
- [PR Template](./.github/pull_request_template.md) — Pull request guidelines

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with your API keys

# Run
python -m masterclaw_core
```

## API Documentation 📚

MasterClaw Core provides interactive API documentation:

| Documentation | URL | Description |
|---------------|-----|-------------|
| **Swagger UI** | `http://localhost:8000/docs` | Interactive API explorer with "Try it out" feature |
| **ReDoc** | `http://localhost:8000/redoc` | Clean, responsive API reference documentation |
| **OpenAPI Schema** | `http://localhost:8000/openapi.json` | Raw OpenAPI 3.0 specification |

### Using Swagger UI

1. Navigate to `http://localhost:8000/docs`
2. Browse available endpoints by category
3. Click "Try it out" to test endpoints directly from the browser
4. View request/response schemas and example payloads

## API Endpoints

### Health
```bash
GET /health
```

### Security Health Check
```bash
GET /health/security
```

Returns security configuration status:
- `status`: "secure" or "insecure"
- `environment`: Current environment (development/production)
- `issues_count`: Number of security issues detected
- `recommendations_count`: Number of configuration recommendations

### Metrics (Prometheus)
```bash
GET /metrics
```

Returns Prometheus-formatted metrics for monitoring:
- `masterclaw_http_requests_total` - Total HTTP requests by method, endpoint, status
- `masterclaw_http_request_duration_seconds` - Request latency histogram
- `masterclaw_chat_requests_total` - Chat requests by provider and model
- `masterclaw_chat_tokens_total` - Token usage counter
- `masterclaw_memory_operations_total` - Memory operations by type and status
- `masterclaw_memory_search_duration_seconds` - Memory search latency
- `masterclaw_active_sessions` - Gauge of active sessions
- `masterclaw_memory_entries_total` - Gauge of total memory entries
- `masterclaw_llm_requests_total` - LLM API requests by provider
- `masterclaw_llm_request_duration_seconds` - LLM request latency

### Chat
```bash
POST /v1/chat
{
  "message": "Hello, MasterClaw!",
  "session_id": "abc123",
  "provider": "openai",
  "model": "gpt-4",
  "use_memory": true
}
```

### Memory
```bash
# Search memories
POST /v1/memory/search
{
  "query": "backup strategy",
  "top_k": 5
}

# Add memory
POST /v1/memory/add
{
  "content": "Remember to backup daily",
  "metadata": {"priority": "high"},
  "source": "user_instruction"
}

# Get memory
GET /v1/memory/{memory_id}

# Delete memory
DELETE /v1/memory/{memory_id}
```

### Sessions
```bash
# List all sessions
GET /v1/sessions?limit=100&active_since_hours=24

# Get session chat history
GET /v1/sessions/{session_id}?limit=50

# Delete a session and all its messages
DELETE /v1/sessions/{session_id}

# Get session statistics
GET /v1/sessions/stats/summary
```

### Maintenance API 🆕

System maintenance operations for administration:

```bash
# Get maintenance status
GET /v1/maintenance/status?retention_days=30

# Run maintenance tasks
POST /v1/maintenance/run
{
  "task": "health_history_cleanup",
  "days": 30,
  "dry_run": false
}
```

**Available Tasks:**
- `health_history_cleanup` - Remove old health history records
- `cache_clear` - Clear the response cache
- `session_cleanup` - Remove old sessions
- `memory_optimize` - Optimize memory store
- `all` - Run all maintenance tasks

**Features:**
- Dry-run mode for safe previews
- Configurable retention period
- Detailed results for each task
- Maintenance recommendations

### Cache API 🆕

Response caching management:

```bash
# Get cache statistics
GET /cache/stats

# Get cache health
GET /cache/health

# Clear all cached responses
POST /cache/clear
```

### Logs API 🆕

Real-time log streaming and retrieval:

```bash
# Stream logs (SSE)
POST /v1/logs/stream
{
  "service": "core",
  "level": "INFO",
  "search": "error",
  "follow": true
}

# Get recent logs
GET /v1/logs?service=core&level=ERROR&since=1h&limit=100
```

### Context API (rex-deus Integration) 🆕

Access Rex's personal context files programmatically:

```bash
# Get projects
GET /v1/context/projects?status=active&priority=high

# Get goals
GET /v1/context/goals?status=active

# Get people
GET /v1/context/people?role=developer

# Get knowledge entries
GET /v1/context/knowledge?category=technology

# Get preferences
GET /v1/context/preferences?category=communication

# Search across all context
GET /v1/context/search?query=masterclaw

# Get context summary
GET /v1/context/summary
```

**Use Cases:**
- Personalized responses based on Rex's preferences
- Query active projects and goals
- Knowledge base lookups
- People and relationship context

## CLI Integration 🆕

The MasterClaw CLI (`mc`) provides convenient access to maintenance operations:

```bash
# Check maintenance status
mc api-maintenance status

# Run maintenance with dry-run preview
mc api-maintenance run --task health_history_cleanup --dry-run

# Actually run maintenance
mc api-maintenance run --task all --days 30

# List available tasks
mc api-maintenance tasks
```

## Architecture

```
masterclaw_core/
├── __init__.py           # Package info
├── __main__.py           # Entry point
├── main.py               # FastAPI app
├── config.py             # Settings with validation
├── models.py             # Pydantic models
├── llm.py                # LLM router (OpenAI, Anthropic)
├── memory.py             # Memory store (Chroma, JSON)
├── cache.py              # Response caching (Redis/Memory)
├── health_history.py     # Health tracking and analytics
├── audit_logger.py       # Security audit logging
└── context_manager.py    # Rex-deus context integration
```

## Configuration

Configuration is validated on startup with security checks:

| Variable | Default | Description | Validation |
|----------|---------|-------------|------------|
| `OPENAI_API_KEY` | - | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | - | Anthropic API key | - |
| `DEFAULT_MODEL` | gpt-4 | Default LLM model | - |
| `MEMORY_BACKEND` | chroma | Memory backend | Must be: chroma, json |
| `CHROMA_PERSIST_DIR` | ./data/chroma | ChromaDB directory | - |
| `PORT` | 8000 | API port | 1-65535 |
| `RATE_LIMIT_PER_MINUTE` | 60 | Rate limit per IP | 1-10000 |
| `CORS_ORIGINS` | ["*"] | Allowed CORS origins | Valid URLs; warns if "*" in production |
| `SESSION_TIMEOUT` | 3600 | Session timeout (seconds) | 60-604800 (7 days) |
| `LOG_LEVEL` | info | Logging level | debug, info, warning, error, critical |
| `CACHE_ENABLED` | true | Enable response caching | true/false |
| `CACHE_BACKEND` | memory | Cache backend | memory, redis |
| `CACHE_DEFAULT_TTL` | 300 | Default cache TTL (seconds) | 0-86400 |
| `CACHE_MAX_SIZE` | 1000 | Max entries in memory cache | 100-100000 |
| `CACHE_REDIS_URL` | - | Redis connection URL | Valid redis:// URL |
| `ENVIRONMENT` | development | Environment name | development, production |

### Security Validation

The configuration system includes security validators:

- **PORT**: Must be a valid port number (1-65535)
- **RATE_LIMIT_PER_MINUTE**: Must be reasonable (1-10000)
- **CORS_ORIGINS**: Warns if `*` is used in production; validates URL format
- **SESSION_TIMEOUT**: Must be between 1 minute and 7 days
- **LOG_LEVEL**: Must be a standard log level
- **MEMORY_BACKEND**: Must be a supported backend

On startup in production mode, security issues are logged as warnings.

### Environment Detection

Set `NODE_ENV=production` or `ENV=production` to enable production security checks.

## Docker

```bash
# Build
docker build -t masterclaw-core .

# Run
docker run -p 8000:8000 --env-file .env masterclaw-core
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=masterclaw_core

# Run specific test file
pytest tests/test_config.py -v

# Run API integration tests
pytest tests/test_api.py -v
```

## Development Workflow

### Quick Start for Development

```bash
# 1. Clone and setup
git clone https://github.com/TheMasterClaw/masterclaw-core.git
cd masterclaw-core
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Run the API
python -m masterclaw_core

# 4. In another terminal, use the CLI
mc api-maintenance status
mc status
```

## Ecosystem Integration

MasterClaw Core integrates with other components of the ecosystem:

| Component | Integration | Purpose |
|-----------|-------------|---------|
| **masterclaw-tools** | CLI commands | Remote administration via `mc` |
| **masterclaw-infrastructure** | Docker Compose | Deployment and orchestration |
| **level100-studios** | Design system | UI components for interfaces |
| **rex-deus** | Context API | Personal context and preferences |

## Ecosystem Overview 🌐

### masterclaw-tools CLI Commands

The MasterClaw CLI (`mc`) provides comprehensive system administration:

| Command | Description |
|---------|-------------|
| `mc status` | Dashboard-style service status monitoring |
| `mc health` | Detailed health monitoring with history and trends |
| `mc doctor` | System diagnostics and recommendations |
| `mc logs` | View and stream logs from services |
| `mc api-maintenance` | Remote maintenance operations |
| `mc whoami` | User context and system information |
| `mc workflow` | Workflow automation |
| `mc terraform` | Infrastructure management |

### level100-studios Design System Components

The design system now includes 20+ production-ready components:

**Layout & Navigation:**
- `Divider` - Visual content separators
- `Breadcrumbs` - Navigation path indicators
- `Tabs` - Tabbed content interface
- `Accordion` - Collapsible content sections

**Data Display:**
- `Table` - Tabular data display with sorting
- `Stat` - Statistics and metrics display
- `Timeline` - Chronological events
- `Progress` - Progress bars
- `Skeleton` - Loading placeholders

**Input & Selection:**
- `Button` - Action buttons
- `Input` - Text input fields
- `Select` - Dropdown selection
- `Switch` - Toggle switches
- `Radio` - Single-select options
- `Checkbox` - Multi-select options

**Feedback & Status:**
- `Alert` - Important messages and notifications
- `Toast` - Notification toasts
- `Spinner` - Loading indicators
- `Badge` - Status indicators and labels
- `Chip` - Labels, tags, and filters
- `EmptyState` - Empty list/page states

**Utility:**
- `Modal` - Dialog and overlay component
- `Tooltip` - Hover information tooltips
- `Avatar` - User/profile avatars
- `Kbd` - Keyboard key representations
- `Code` - Inline code and code blocks

### API Features

**Core API Endpoints:**
- Chat with memory integration
- Memory store (search, add, delete, update)
- Session management
- Bulk operations (memory, sessions)
- Maintenance operations
- Real-time log streaming (SSE)
- Health monitoring and history
- Security health checks
- Prometheus metrics
- Cache management

**New Bulk Operations:**
- `POST /v1/memory/bulk-delete` - Batch delete memories
- `POST /v1/memory/bulk-update` - Batch update metadata
- `POST /v1/sessions/batch-archive` - Archive sessions
- `GET /v1/memory/stats/bulk` - Memory statistics
- `GET /v1/sessions/stats/batch` - Session statistics

---

*The brain behind the claw.* 🐾
