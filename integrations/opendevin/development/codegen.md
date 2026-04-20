# Code Generation Workflows

## Overview

This document describes the code generation workflows available through OpenDevin integration, enabling automated code creation from natural language specifications.

## Generation Types

### 1. New Code Generation

Generate new code from scratch based on specifications.

```yaml
generation:
  type: new
  spec: |
    Create a Python FastAPI application with:
    - User authentication endpoint
    - JWT token validation
    - Password hashing with bcrypt
  language: python
  framework: fastapi
  output: ./generated/app
```

### 2. Code Completion

Complete partial code based on context.

```yaml
generation:
  type: completion
  input: ./src/partial.py
  context:
    - ./src/similar_files/
  max_tokens: 1000
```

### 3. Code Modification

Modify existing code according to change requests.

```yaml
generation:
  type: modification
  input: ./src/main.py
  change: "Add error handling and logging to all functions"
  preserve: 
    - function_signatures
    - public_api
```

### 4. Code Refactoring

Refactor code for specific goals.

```yaml
generation:
  type: refactoring
  input: ./src/legacy.py
  goal: improve_performance
  constraints:
    - preserve_behavior
    - maintain_compatibility
```

## Workflow Patterns

### Waterfall Generation

Sequential generation with validation at each step:

```python
from openclaw.integrations.opendevin import CodeGenerator

gen = CodeGenerator()

# Step 1: Generate structure
structure = gen.generate_structure(
    spec="E-commerce API",
    components=["users", "products", "orders", "payments"]
)

# Step 2: Generate code for each component
for component in structure.components:
    code = gen.generate_component(
        component=component,
        template="api_module"
    )
    gen.write(component.path, code)

# Step 3: Generate tests
tests = gen.generate_tests(structure)

# Step 4: Generate documentation
docs = gen.generate_docs(structure)
```

### Iterative Generation

Generate with feedback loops:

```python
gen = CodeGenerator()

# Initial generation
result = gen.generate(spec="Create a REST API")

# Validate
validation = gen.validate(result)

# Iterate based on feedback
while not validation.passed:
    result = gen.refine(
        previous=result,
        feedback=validation.feedback
    )
    validation = gen.validate(result)
```

### Test-Driven Generation

Generate code from tests:

```python
gen = CodeGenerator()

# Write tests first
tests = """
def test_user_registration():
    response = client.post('/register', json={
        'username': 'test',
        'password': 'password123'
    })
    assert response.status_code == 201
"""

# Generate implementation to pass tests
implementation = gen.generate_from_tests(
