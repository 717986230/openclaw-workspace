# Sandbox Environment Setup

## Overview

Sandbox environments provide isolated execution contexts for code generation and testing, ensuring safety and reproducibility.

## Sandbox Types

### 1. Docker Sandbox

Container-based isolation for maximum security.

```yaml
sandbox:
  type: docker
  image: python:3.11-slim
  
  # Resource limits
  resources:
    cpu_limit: "2"
    memory_limit: "2g"
    disk_limit: "10g"
    time_limit: "1h"
    
  # Network configuration
  network:
    enabled: false  # Isolated by default
    allowed_hosts:
      - pypi.org
      - npmjs.org
      
  # Volume mounts
  volumes:
    - host: ./workspace
      container: /workspace
      mode: rw
    - host: ./cache
      container: /cache
      mode: ro
```

### 2. Process Sandbox

Lightweight process-level isolation.

```yaml
sandbox:
  type: process
  
  isolation:
    filesystem: true  # Chroot-like isolation
    network: true     # Network namespace
    user: true        # User namespace
    
  # Resource limits
  rlimits:
    RLIMIT_NOFILE: 1024
    RLIMIT_NPROC: 100
    RLIMIT_AS: 2147483648  # 2GB
```

### 3. WebContainer Sandbox

Browser-based sandbox for web projects.

```yaml
sandbox:
  type: webcontainer
  
  runtime:
    node_version: "18"
    package_manager: "pnpm"
    
  features:
    filesystem: true
    terminal: true
    preview: true
```

## Security Configuration

### User Isolation

```yaml
security:
  # Run as non-root user
  user:
    uid: 1000
    gid: 1000
    
  # Capability dropping
  capabilities:
    drop:
      - ALL
    add:
      - CHOWN
      - SETUID
      - SETGID
      
  # Seccomp filtering
  seccomp:
    profile: default
    allow:
      - read
      - write
      - open
      - close
      - mmap
      - munmap
```

### Filesystem Isolation

```yaml
filesystem:
  # Allowed paths
  allowed_paths:
    - /workspace
    - /tmp
    - /cache
    
  # Blocked paths
  blocked_paths:
    - /etc/passwd
    - /etc/shadow
    - ~/.ssh
    - ~/.gnupg
    
  # Read-only paths
  read_only_paths:
    - /usr
    - /lib
    - /bin
```

### Network Isolation

```yaml
network:
  # Outbound rules
  outbound:
    default: deny
    allow:
      - domain: pypi.org
        ports: [443]
      - domain: npmjs.org
        ports: [443]
        
  # Inbound rules (typically blocked)
  inbound:
    default: deny
    
  # DNS configuration
  dns:
    servers:
      - 8.8.8.8
      - 8.8.4.4
```

## Resource Management

### CPU Management

```yaml
resources:
  cpu:
    # CPU quota
    quota: 200000  # 2 CPUs
    period: 100000
    
    # CPU shares (relative weight)
    shares: 1024
    
    # CPU pinning (specific cores)
    cpus: "0-1"
```

### Memory Management

```yaml
resources:
  memory:
    # Hard limit
    limit: 2g
    
    # Soft limit
    reservation: 512m
    
    # Swap limit
    swap: 1g
    
    # OOM killer behavior
    oom_kill_disable: false
```

### Disk Management

```yaml
resources:
  disk:
    # Quota
    quota: 10g
    
    # I/O limits
    io_limits:
      read_bps: 104857600   # 100 MB/s
      write_bps: 52428800   # 50 MB/s
      read_iops: 1000
      write_iops: 500
```

## Lifecycle Management

### Sandbox Creation

```python
from openclaw.integrations.opendevin import SandboxManager

manager = SandboxManager()

# Create sandbox
sandbox = manager.create(
    name="dev-session-1",
    config={
        "type": "docker",
        "image": "python:3.11",
        "resources": {
            "memory": "2g",
            "cpu": "2"
        }
    }
)
```

### Session Management

```python
# Start sandbox
sandbox.start()

# Execute commands
result = sandbox.execute("pip install fastapi")

# Check status
status = sandbox.status()
print(f"Running: {status.running}, Memory: {status.memory_usage}")

# Pause/Resume
sandbox.pause()
sandbox.resume()

# Stop sandbox
sandbox.stop()

# Clean up
sandbox.destroy()
```

### Snapshot & Restore

```python
# Create snapshot
snapshot = sandbox.snapshot(name="before-refactor")

# Make changes
sandbox.execute("python refactor.py")

# If something goes wrong, restore
sandbox.restore(snapshot)

# List snapshots
snapshots = sandbox.list_snapshots()
```

## Monitoring

### Health Checks

```yaml
monitoring:
  health_check:
    interval: 10s
    timeout: 5s
    retries: 3
    
    checks:
      - type: command
        test: "echo 'healthy'"
      - type: http
        endpoint: /health
        port: 8000
      - type: process
        name: python
```

### Metrics Collection

```yaml
monitoring:
  metrics:
    collect:
      - cpu_usage
      - memory_usage
      - disk_usage
      - network_io
      - process_count
      
    export:
      - prometheus
      - openclaw-metrics
      
    interval: 15s
```

### Logging

```yaml
logging:
  # Container logs
  container:
    driver: json-file
    options:
      max-size: "10m"
      max-file: "3"
      
  # Application logs
  application:
    level: INFO
    format: json
    output: /var/log/app.log
```

## Best Practices

### 1. Resource Allocation

- Start with conservative limits
- Monitor usage patterns
- Adjust based on actual needs
- Plan for peak loads

### 2. Security Hardening

- Use minimal base images
- Run as non-root user
- Limit network access
- Drop unnecessary capabilities

### 3. Cleanup

- Implement automatic cleanup
- Remove unused containers
- Prune old images
- Archive logs periodically

## Example Configurations

### Python Development

```yaml
sandbox:
  type: docker
  image: python:3.11-slim
  
  setup:
    - pip install pytest black mypy
    
  resources:
    memory: 2g
    cpu: 2
    
  volumes:
    - ./src:/workspace/src:rw
    - ./tests:/workspace/tests:rw
```

### Node.js Development

```yaml
sandbox:
  type: docker
  image: node:18-alpine
  
  setup:
    - npm install -g typescript jest
    
  resources:
    memory: 2g
    cpu: 2
    
  volumes:
    - ./src:/workspace/src:rw
    - ./package.json:/workspace/package.json:ro
```

### Multi-language Project

```yaml
sandbox:
  type: docker
  image: ubuntu:22.04
  
  setup:
    - apt-get update
    - apt-get install -y python3 nodejs npm
    
  resources:
    memory: 4g
    cpu: 4
    
  volumes:
    - ./src:/workspace:rw
```

## Troubleshooting

### Common Issues

**1. Container fails to start**
- Check Docker daemon status
- Verify image availability
- Check resource availability
- Review security constraints

**2. Permission denied errors**
- Check user ID mapping
- Verify file permissions
- Check SELinux/AppArmor policies

**3. Resource exhaustion**
- Increase limits
- Optimize code
- Check for memory leaks
- Monitor actual usage

### Debug Commands

```bash
# Check sandbox status
openclaw sandbox status <name>

# View sandbox logs
openclaw sandbox logs <name> --tail 100

# Inspect sandbox details
openclaw sandbox inspect <name>

# Execute debug shell
openclaw sandbox exec <name> -- /bin/sh
```

## References

- [Docker Setup Guide](../environment/docker-setup.md)
- [Environment Manager](../environment/env-manager.md)
- [Security Configuration](../../docs/security.md)
