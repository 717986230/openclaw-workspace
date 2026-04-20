# Environment Lifecycle Management

## Overview

The Environment Manager handles the complete lifecycle of development and testing environments, from creation to cleanup.

## Lifecycle Phases

### 1. Creation

Initialize new environments from templates or configurations.

```python
from openclaw.integrations.opendevin import EnvironmentManager

manager = EnvironmentManager()

# Create from template
env = manager.create(
    name="dev-env-1",
    template="python-fastapi",
    config={
        "python_version": "3.11",
        "packages": ["fastapi", "uvicorn", "pytest"]
    }
)

# Create from scratch
env = manager.create(
    name="custom-env",
    base_image="ubuntu:22.04",
    setup_scripts=["install_dependencies.sh"]
)
```

### 2. Configuration

Apply configuration after creation.

```python
# Configure environment variables
env.set_env({
    "DATABASE_URL": "postgresql://localhost/db",
    "DEBUG": "true"
})

# Install packages
env.install_packages(["numpy", "pandas"])

# Setup services
env.start_service("redis")
env.start_service("postgresql")

# Configure network
env.expose_port(8000)
env.set_hostname("dev-server")
```

### 3. Usage

Active environment usage during development.

```python
# Execute commands
result = env.execute("python manage.py migrate")

# Run code
output = env.run_code("""
import fastapi
app = fastapi.FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}
""")

# Interactive shell
shell = env.shell()
shell.send("python")
shell.send("print('hello')")
shell.close()
```

### 4. Snapshotting

Save environment state for later restoration.

```python
# Create snapshot
snapshot = env.snapshot(name="before-migration")

# List snapshots
snapshots = env.list_snapshots()
for snap in snapshots:
    print(f"{snap.name} - {snap.timestamp}")

# Restore snapshot
env.restore("before-migration")

# Delete snapshot
env.delete_snapshot("old-snapshot")
```

### 5. Export/Import

Share environments between systems.

```python
# Export environment
env.export(path="./dev-env.tar.gz")

# Import environment
env2 = manager.import_env(
    path="./dev-env.tar.gz",
    name="imported-env"
)

# Export as image
env.export_image(name="my-dev-env:v1")
```

### 6. Cleanup

Proper resource cleanup.

```python
# Stop environment
env.stop()

# Destroy environment (with confirmation)
env.destroy(confirm=True)

# Force cleanup
env.force_cleanup()

# Clean up all stopped environments
manager.cleanup_stopped()
```

## Environment Templates

### Built-in Templates

```yaml
templates:
  python-fastapi:
    base: python:3.11-slim
    setup:
      - pip install fastapi uvicorn pytest
    services: []
    ports: [8000]
    
  python-django:
    base: python:3.11
    setup:
      - pip install django djangorestframework pytest-django
    services: [postgresql]
    ports: [8000, 5432]
    
  node-express:
    base: node:18
    setup:
      - npm install express jest
    services: []
    ports: [3000]
    
  full-stack:
    base: ubuntu:22.04
    setup:
      - apt-get install -y python3 nodejs npm postgresql
      - pip3 install fastapi
      - npm install -g typescript
    services: [postgresql, redis]
    ports: [3000, 8000]
```

### Custom Templates

```yaml
# templates/custom.yaml
name: my-custom-template
description: Custom template for ML projects

base:
  image: python:3.11
  setup:
    - pip install torch torchvision jupyter

services:
  - name: jupyter
    command: jupyter notebook --ip=0.0.0.0
    ports: [8888]
    
  - name: tensorboard
    command: tensorboard --logdir=/logs
    ports: [6006]

volumes:
  - name: data
    path: /data
  - name: logs
    path: /logs
    
environment:
  PYTHONPATH: /workspace
  JUPYTER_ENABLE_LAB: "yes"
```

## Resource Management

### Allocation

```python
# Allocate resources
env.allocate_resources(
    cpu=2,
    memory="4g",
    disk="20g",
    gpu=1  # Optional
)

# Check allocation
allocation = env.get_allocation()
print(f"CPU: {allocation.cpu}, Memory: {allocation.memory}")

# Update allocation
env.update_allocation(memory="8g")
```

### Monitoring

```python
# Real-time monitoring
metrics = env.monitor()
print(f"""
CPU: {metrics.cpu_percent}%
Memory: {metrics.memory_used}/{metrics.memory_total}
Disk: {metrics.disk_used}/{metrics.disk_total}
Network: {metrics.network_rx}/{metrics.network_tx}
""")

# Historical metrics
history = env.get_metrics_history(
    start="2024-01-01T00:00:00",
    end="2024-01-02T00:00:00",
    interval="5m"
)
```

### Quotas

```yaml
quotas:
  # Global quotas
  global:
    max_environments: 10
    total_cpu: 16
    total_memory: 32g
    total_disk: 500g
    
  # Per-user quotas
  per_user:
    max_environments: 3
    max_cpu: 4
    max_memory: 8g
    max_disk: 50g
```

## Service Management

### Starting Services

```python
# Start service
env.start_service("postgresql", config={
    "version": "14",
    "database": "app_db",
    "user": "app_user"
})

# Start multiple services
env.start_services(["redis", "rabbitmq"])

# Check service status
status = env.service_status("postgresql")
```

### Service Configuration

```yaml
services:
  postgresql:
    image: postgres:14
    environment:
      POSTGRES_DB: app_db
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD", "pg_isready"]
      interval: 10s
      timeout: 5s
      retries: 5
```

### Service Discovery

```python
# Get service endpoint
endpoint = env.get_service_endpoint("postgresql")
# Returns: {"host": "localhost", "port": 5432}

# List all services
services = env.list_services()
for service in services:
    print(f"{service.name}: {service.status}")
```

## Network Configuration

### Network Creation

```python
# Create isolated network
network = env.create_network(
    name="app-network",
    driver="bridge",
    subnet="172.28.0.0/16"
)

# Connect services
env.connect_to_network("app-network", "postgresql")
env.connect_to_network("app-network", "redis")
```

### Port Management

```python
# Expose port
env.expose_port(8000, protocol="tcp")

# Port forwarding
env.forward_port(
    host_port=8080,
    container_port=8000,
    protocol="tcp"
)

# Get exposed ports
ports = env.get_exposed_ports()
```

### DNS Configuration

```yaml
dns:
  # Custom DNS servers
  servers:
    - 8.8.8.8
    - 8.8.4.4
    
  # Custom DNS entries
  entries:
    - name: app.local
      ip: 172.28.0.10
    - name: db.local
      ip: 172.28.0.11
```

## State Management

### File System State

```python
# Sync files
env.sync_files(
    source="./src",
    destination="/workspace/src",
    exclude=["*.pyc", "__pycache__"]
)

# Pull files
env.pull_files(
    source="/workspace/output",
    destination="./output"
)

# Watch for changes
env.watch_files(
    path="/workspace",
    callback=lambda event: print(f"File changed: {event.path}")
)
```

### Database State

```python
# Backup database
backup = env.backup_database(
    service="postgresql",
    database="app_db"
)

# Restore database
env.restore_database(
    service="postgresql",
    database="app_db",
    backup=backup
)

# Run migrations
env.run_migrations()
```

## Security

### Access Control

```yaml
security:
  # Authentication
  auth:
    type: token
    token_env: ENV_TOKEN
    
  # Authorization
  rbac:
    roles:
      admin:
        permissions: ["*"]
      developer:
        permissions:
          - env.read
          - env.execute
          - env.write
      viewer:
        permissions:
          - env.read
```

### Audit Logging

```yaml
audit:
  enabled: true
  events:
    - create
    - destroy
    - execute
    - snapshot
    - restore
    
  output:
    - path: /var/log/opendevin/audit.log
      format: json
    - type: openclaw-audit
```

## Best Practices

### 1. Naming Conventions

```
{project}-{environment_type}-{instance_id}

Examples:
- myapp-dev-001
- myapp-test-002
- myapp-staging-001
```

### 2. Resource Cleanup

- Implement automatic cleanup policies
- Use TTL for temporary environments
- Schedule regular cleanup jobs
- Monitor abandoned environments

### 3. Security Hardening

- Use minimal base images
- Run services as non-root
- Limit network access
- Enable audit logging

### 4. Monitoring

- Monitor resource usage
- Set up alerts for quota violations
- Track environment lifecycle events
- Implement health checks
