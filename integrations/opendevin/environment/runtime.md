# Runtime Configuration

## Overview

This document describes the runtime configuration options for OpenDevin integration.

## Configuration File

### Location

Default configuration locations (in order of precedence):
1. `./opendevin.yaml` - Project-specific
2. `~/.opendevin/config.yaml` - User-level
3. `/etc/opendevin/config.yaml` - System-wide

### Configuration Structure

```yaml
# opendevin.yaml

# General settings
general:
  debug: false
  log_level: INFO
  workspace: ./workspace

# Agent configuration
agent:
  type: CodeActAgent
  model: claude-3-opus
  max_iterations: 100
  temperature: 0.7
  
  # Prompt configuration
  prompts:
    system: |
      You are an AI software engineer.
      Write clean, well-tested code.
    user_prefix: "Task: "
    
  # Memory configuration
  memory:
    enabled: true
    max_history: 10
    vector_store: openclaw-memory

# Sandbox configuration
sandbox:
  type: docker
  
  # Container settings
  container:
    image: python:3.11-slim
    user: opendevin
    workdir: /workspace
    
  # Security settings
  security:
    no_new_privileges: true
    read_only_root: false
    capabilities_drop: [ALL]
    
  # Resource limits
  limits:
    memory: 2g
    cpu: 2
    disk: 10g
    time: 3600

# Execution settings
execution:
  timeout:
    command: 60
    task: 600
    total: 3600
    
  retry:
    max_retries: 3
    delay: 5
    
  parallel:
    enabled: true
    max_workers: 4

# Testing configuration
testing:
  framework: auto  # auto-detect
  
  coverage:
    enabled: true
    threshold: 80
    report_format: html
    
  parallel:
    enabled: true
    workers: auto
    
  markers:
    skip_ci: [slow, integration]
    required: [unit]

# Output settings
output:
  format: json
  color: true
  verbose: false
  
  logs:
    path: ./logs
    rotation: daily
    retention: 7
    
  reports:
    path: ./reports
    formats: [html, junit-xml]
```

## Environment Variables

### Agent Configuration

```bash
# Model selection
OPENDEVIN_MODEL=claude-3-opus

# Agent type
OPENDEVIN_AGENT_TYPE=CodeActAgent

# Maximum iterations
OPENDEVIN_MAX_ITERATIONS=100

# Temperature
OPENDEVIN_TEMPERATURE=0.7
```

### Sandbox Configuration

```bash
# Sandbox type
OPENDEVIN_SANDBOX_TYPE=docker

# Docker image
OPENDEVIN_DOCKER_IMAGE=python:3.11-slim

# Resource limits
OPENDEVIN_MEMORY_LIMIT=2g
OPENDEVIN_CPU_LIMIT=2

# Timeout
OPENDEVIN_TIMEOUT=3600
```

### Testing Configuration

```bash
# Test framework
OPENDEVIN_TEST_FRAMEWORK=pytest

# Coverage threshold
OPENDEVIN_COVERAGE_THRESHOLD=80

# Parallel execution
OPENDEVIN_TEST_PARALLEL=true
```

### Logging

```bash
# Log level
OPENDEVIN_LOG_LEVEL=INFO

# Debug mode
OPENDEVIN_DEBUG=false

# Log path
OPENDEVIN_LOG_PATH=./logs
```

## Runtime Profiles

### Development Profile

```yaml
# profiles/development.yaml
profile: development

agent:
  model: claude-3-sonnet
  temperature: 0.7
  
sandbox:
  limits:
    memory: 4g
    cpu: 4
    
execution:
  timeout:
    total: 7200
    
output:
  verbose: true
  log_level: DEBUG
```

### Production Profile

```yaml
# profiles/production.yaml
profile: production

agent:
  model: claude-3-opus
  temperature: 0.3
  
sandbox:
  security:
    no_new_privileges: true
    read_only_root: true
    
execution:
  timeout:
    total: 1800
    
output:
  log_level: WARNING
  verbose: false
```

### CI/CD Profile

```yaml
# profiles/ci.yaml
profile: ci

agent:
  model: claude-3-sonnet
  max_iterations: 50
  
testing:
  coverage:
    threshold: 80
    fail_below: true
    
execution:
  timeout:
    total: 1800
    
output:
  format: junit-xml
  reports:
    path: ./test-results
```

## Model Configuration

### Claude Models

```yaml
models:
  claude-3-opus:
    provider: anthropic
    max_tokens: 200000
    supports_vision: true
    
  claude-3-sonnet:
    provider: anthropic
    max_tokens: 180000
    supports_vision: true
    
  claude-3-haiku:
    provider: anthropic
    max_tokens: 150000
    supports_vision: true
```

### GPT Models

```yaml
models:
  gpt-4:
    provider: openai
    max_tokens: 128000
    
  gpt-4-turbo:
    provider: openai
    max_tokens: 128000
    
  gpt-3.5-turbo:
    provider: openai
    max_tokens: 16000
```

### Local Models

```yaml
models:
  local-llama:
    provider: local
    endpoint: http://localhost:11434/api
    model: llama2
    
  local-codellama:
    provider: local
    endpoint: http://localhost:11434/api
    model: codellama
```

## Security Configuration

### Authentication

```yaml
security:
  authentication:
    enabled: true
    type: api_key
    key_env: OPENDEVIN_API_KEY
    
  # Or OAuth
  oauth:
    provider: auth0
    domain: your-domain.auth0.com
    audience: https://api.opendevin.dev
```

### Authorization

```yaml
security:
  authorization:
    enabled: true
    type: rbac
    
    roles:
      admin:
        permissions: ["*"]
      developer:
        permissions:
          - agent.run
          - sandbox.create
          - tests.run
      viewer:
        permissions:
          - agent.status
          - results.view
```

### Audit Logging

```yaml
security:
  audit:
    enabled: true
    events:
      - agent.start
      - agent.stop
      - sandbox.create
      - sandbox.destroy
      - file.write
      - command.execute
      
    output:
      - type: file
        path: /var/log/opendevin/audit.log
        format: json
      - type: syslog
        facility: local0
```

## Network Configuration

### Proxy Settings

```yaml
network:
  proxy:
    http: http://proxy.example.com:8080
    https: http://proxy.example.com:8080
    no_proxy:
      - localhost
      - 127.0.0.1
      - .internal.example.com
```

### DNS Configuration

```yaml
network:
  dns:
    servers:
      - 8.8.8.8
      - 8.8.4.4
      
    search_domains:
      - internal.example.com
```

### Firewall Rules

```yaml
network:
  firewall:
    outbound:
      default: deny
      allow:
        - domain: pypi.org
          ports: [443]
        - domain: github.com
          ports: [443, 22]
          
    inbound:
      default: deny
```

## Performance Tuning

### Caching

```yaml
performance:
  cache:
    enabled: true
    type: redis
    host: localhost
    port: 6379
    ttl: 3600
    
    # What to cache
    cache_prompts: true
    cache_embeddings: true
    cache_results: true
```

### Connection Pooling

```yaml
performance:
  connections:
    pool_size: 10
    max_overflow: 20
    pool_timeout: 30
```

### Memory Management

```yaml
performance:
  memory:
    max_usage: 80%  # of limit
    gc_threshold: 70%
    clear_interval: 300  # seconds
```

## Troubleshooting

### Common Configuration Issues

1. **Configuration not found**
   - Check file location
   - Verify file permissions
   - Use absolute paths

2. **Environment variables not loaded**
   - Check variable names (OPENDEVIN_*)
   - Verify shell configuration
   - Use export in scripts

3. **Profile not applied**
   - Check profile name
   - Verify profile file exists
   - Use --profile flag explicitly

### Validation

```bash
# Validate configuration
openclaw opendevin config validate

# Show effective configuration
openclaw opendevin config show

# Test configuration
openclaw opendevin config test
```
