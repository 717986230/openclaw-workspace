# Development Agent Configuration

## Overview

The Development Agent is the core OpenDevin component responsible for code generation and modification tasks. This document describes its configuration and usage within OpenClaw.

## Agent Types

### CodeActAgent
Primary agent for general-purpose coding tasks.

**Capabilities:**
- Code generation from specifications
- File system operations
- Command execution
- Web browsing for documentation

**Configuration:**
```yaml
agent:
  type: CodeActAgent
  model: claude-3-opus
  max_iterations: 100
  temperature: 0.7
  
  # Action space configuration
  actions:
    - file_read
    - file_write
    - file_delete
    - command_run
    - browse
    
  # Constraints
  constraints:
    max_file_size: 1MB
    max_files: 100
    max_commands_per_iteration: 10
```

### PlannerAgent
Agent specialized in planning and task decomposition.

**Capabilities:**
- Task breakdown into subtasks
- Dependency analysis
- Progress tracking
- Multi-step planning

**Configuration:**
```yaml
agent:
  type: PlannerAgent
  model: claude-3-opus
  
  planning:
    max_depth: 5
    enable_refinement: true
    
  subagents:
    - type: CodeActAgent
      tasks: ["implementation"]
    - type: TestAgent
      tasks: ["testing"]
```

### ManagerAgent
Agent for coordinating multiple specialized agents.

**Capabilities:**
- Agent orchestration
- Task distribution
- Result aggregation
- Conflict resolution

**Configuration:**
```yaml
agent:
  type: ManagerAgent
  
  team:
    - type: CodeActAgent
      name: "developer"
      specialty: "implementation"
    - type: TestAgent
      name: "tester"
      specialty: "testing"
    - type: ReviewAgent
      name: "reviewer"
      specialty: "code_review"
      
  coordination:
    mode: "sequential"  # or "parallel"
    max_parallel_agents: 3
```

## Agent Lifecycle

### 1. Initialization
```python
from openclaw.integrations.opendevin import create_agent

agent = create_agent(
    agent_type="CodeActAgent",
    model="claude-3-opus",
    environment="docker"
)
```

### 2. Task Execution
```python
# Step-by-step execution
result = agent.step(
    task="Create a Python function to calculate fibonacci numbers",
    context={
        "language": "python",
        "style": "functional"
    }
)

# Full task execution
result = agent.run(
    task="Create a REST API for user management",
    max_iterations=100
)
```

### 3. Termination
```python
# Clean shutdown
agent.close()

# Force termination
agent.terminate(timeout=30)
```

## Memory Integration

### Short-term Memory
Maintains context during task execution:
```yaml
memory:
  type: short_term
  max_tokens: 16000
  include_files: true
  include_commands: true
```

### Long-term Memory
Persists across sessions:
```yaml
memory:
  type: long_term
  backend: openclaw-vector-store
  embedding: openai-ada-002
  persist: true
```

### Memory Tools
```python
# Store important information
agent.memory.store(
    key="project_structure",
    value=project_structure,
    metadata={"type": "architecture"}
)

# Retrieve relevant context
context = agent.memory.retrieve(
    query="authentication flow",
    top_k=5
)
```

## Action Handlers

### File Operations
```python
# Read file
content = agent.fs.read_file("src/main.py")

# Write file
agent.fs.write_file(
    path="src/utils.py",
    content=utils_code,
    create_dirs=True
)

# Delete file
agent.fs.delete_file("src/old_module.py")

# List directory
files = agent.fs.list_dir("src/")
```

### Command Execution
```python
# Run command
result = agent.cmd.run(
    command="pip install fastapi",
    timeout=60,
    capture_output=True
)

# Run with environment variables
result = agent.cmd.run(
    command="npm test",
    env={"NODE_ENV": "test"},
    cwd="/workspace/project"
)
```

### Web Browsing
```python
# Fetch documentation
doc = agent.web.fetch("https://fastapi.tiangolo.com/tutorial/")

# Search for information
results = agent.web.search("python async best practices")
```

## Error Handling

### Automatic Recovery
```yaml
error_handling:
  retry_count: 3
  retry_delay: 5
  
  recovery_strategies:
    - type: retry
      conditions:
        - "connection_error"
        - "timeout"
    - type: rollback
      conditions:
        - "syntax_error"
    - type: replan
      conditions:
        - "constraint_violation"
```

### Manual Intervention
```python
# Enable human-in-the-loop
agent.enable_intervention(
    triggers=["syntax_error", "test_failure"],
    timeout=300
)

# Handle intervention
def handle_intervention(event):
    if event.type == "test_failure":
        return {"action": "fix_tests"}
    return {"action": "continue"}

agent.on_intervention(handle_intervention)
```

## Performance Optimization

### Caching
```yaml
optimization:
  cache:
    enabled: true
    backend: redis
    ttl: 3600
    
    # Cache prompt responses
    prompt_cache: true
    
    # Cache file reads
    file_cache: true
```

### Parallelization
```yaml
optimization:
  parallel:
    enabled: true
    max_workers: 4
    
    # Parallelize independent tasks
    strategy: "independent_tasks"
```

### Model Selection
```yaml
model_routing:
  - model: claude-3-haiku
    tasks:
      - "file_operations"
      - "simple_edits"
  - model: claude-3-opus
    tasks:
      - "complex_generation"
      - "architecture_design"
```

## Monitoring

### Metrics Collection
```yaml
monitoring:
  metrics:
    - iterations_total
    - tokens_used
    - files_modified
    - commands_run
    - errors_count
    - execution_time
    
  export:
    - prometheus
    - openclaw-metrics
```

### Logging
```yaml
logging:
  level: INFO
  format: json
  
  handlers:
    - type: file
      path: logs/opendevin.log
      rotation: daily
    - type: openclaw-audit
      events: ["file_write", "command_run"]
```

## Best Practices

1. **Clear Specifications**: Provide detailed task specifications
2. **Iterative Refinement**: Break large tasks into smaller steps
3. **Validation**: Always validate generated code
4. **Testing**: Run tests after code generation
5. **Review**: Enable code review for critical changes

## Example Workflow

```python
# Complete development workflow
agent = create_agent("CodeActAgent")

# 1. Plan the task
plan = agent.plan("Create a user authentication system")

# 2. Execute with monitoring
with agent.monitor() as monitor:
    result = agent.execute(plan)
    
    # 3. Validate results
    if result.success:
        validation = agent.validate(result.output)
        
        # 4. Run tests
        tests = agent.run_tests(result.output)
        
        # 5. Review if needed
        if not tests.passed:
            agent.review_and_fix(tests.failures)

# 6. Generate documentation
agent.generate_docs(result.output)

agent.close()
```

## References

- [Code Generation Workflows](./codegen.md)
- [Sandbox Environment](./sandbox.md)
- [Environment Manager](../environment/env-manager.md)
