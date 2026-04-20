# Docker Environment Setup

## Overview

This guide covers Docker-based environment setup for OpenDevin integration, providing isolated containers for code generation and testing.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- Minimum 4GB RAM available for containers
- 20GB disk space for images

## Basic Setup

### 1. Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  opendevin:
    build:
      context: .
      dockerfile: Dockerfile.opendevin
    container_name: opendevin-agent
    environment:
      - SANDBOX_TYPE=docker
      - LLM_MODEL=claude-3-opus
    volumes:
      - ./workspace:/workspace
      - ./cache:/cache
    networks:
      - opendevin-network
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: false
    tmpfs:
      - /tmp:size=1G,mode=1777
```

### 2. Dockerfile

```dockerfile
# Dockerfile.opendevin
FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash opendevin

# Set working directory
WORKDIR /workspace

# Copy requirements and install
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Switch to non-root user
USER opendevin

# Entry point
ENTRYPOINT ["python", "-m", "opendevin"]
```

## Network Configuration

### Isolated Network

```yaml
networks:
  opendevin-network:
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
          gateway: 172.28.0.1
```

### Network Policies

```yaml
# Network isolation configuration
network:
  # Disable inter-container communication
  icc: false
  
  # Outbound rules
  outbound:
    default: deny
    allow:
      - domain: pypi.org
        ports: [443]
      - domain: npmjs.org
        ports: [443]
      - domain: github.com
        ports: [443, 22]
        
  # No inbound connections
  inbound:
    default: deny
```

## Volume Management

### Volume Configuration

```yaml
volumes:
  # Workspace volume
  workspace:
    driver: local
    driver_opts:
      type: none
      device: ./workspace
      o: bind
      
  # Cache volume (persistent)
  cache:
    driver: local
    
  # Temporary files
  tmp:
    driver: tmpfs
    driver_opts:
      size: 1G
```

### Volume Security

```yaml
# Mount options
volumes:
  workspace:
    mount_options:
      - ro  # Read-only by default
      - nosuid
      - nodev
      - noexec  # No execution from mounted volume
```

## Resource Limits

### Container Resources

```yaml
services:
  opendevin:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
          
    # Additional limits
    ulimits:
      nofile:
        soft: 1024
        hard: 2048
      nproc: 100
```

### Runtime Constraints

```yaml
# Docker runtime options
runtime: runc

# Or use sysbox for stronger isolation
runtime: sysbox-runc

# Health check
healthcheck:
  test: ["CMD", "python", "-c", "import opendevin"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Multi-Container Setup

### Full Development Stack

```yaml
version: '3.8'

services:
  # Main agent container
  opendevin:
    build: .
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/opendevin
    networks:
      - internal
      
  # Redis for caching
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - internal
      
  # PostgreSQL for persistence
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_USER: opendevin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: opendevin
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - internal
      
volumes:
  redis-data:
  postgres-data:
  
networks:
  internal:
    driver: bridge
    internal: true  # No external access
```

## Security Hardening

### 1. User Namespaces

```yaml
# Enable user namespaces
userns-remap: default

# Or specify UID/GID mapping
userns-remap:
  uid: 100000-165535
  gid: 100000-165535
```

### 2. Seccomp Profile

```json
// seccomp-profile.json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "open", "close", "mmap", "munmap"],
      "action": "SCMP_ACT_ALLOW"
    },
    {
      "names": ["execve", "fork", "clone"],
      "action": "SCMP_ACT_ALLOW",
      "args": []
    }
  ]
}
```

```yaml
# Apply seccomp profile
security_opt:
  - seccomp:seccomp-profile.json
```

### 3. AppArmor/SELinux

```yaml
# AppArmor profile
security_opt:
  - apparmor:opendevin-profile

# SELinux context (RHEL/CentOS)
security_opt:
  - label:user:opendevin
  - label:role:opendevin_r
  - label:type:opendevin_t
```

## Image Management

### Building Images

```bash
# Build base image
docker build -t opendevin-base:latest -f Dockerfile.base .

# Build with build args
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg MODEL=claude-3-opus \
  -t opendevin:latest .
```

### Image Scanning

```bash
# Scan for vulnerabilities
docker scout cves opendevin:latest

# Using Trivy
trivy image opendevin:latest

# Using Clair
clair-scanner opendevin:latest
```

### Image Signing

```bash
# Sign image with Docker Content Trust
export DOCKER_CONTENT_TRUST=1
docker push opendevin:latest

# Verify signature
docker trust inspect opendevin:latest
```

## Container Lifecycle

### Starting Containers

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d opendevin

# Start with rebuild
docker-compose up -d --build
```

### Managing Containers

```bash
# View logs
docker-compose logs -f opendevin

# Execute command in container
docker-compose exec opendevin bash

# Check container status
docker-compose ps

# View resource usage
docker stats opendevin-agent
```

### Stopping Containers

```bash
# Stop all services
docker-compose down

# Stop with volume cleanup
docker-compose down -v

# Stop with image cleanup
docker-compose down --rmi all
```

## Monitoring

### Prometheus Integration

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9323']
        
  - job_name: 'opendevin'
    static_configs:
      - targets: ['opendevin:9090']
```

### Grafana Dashboard

```yaml
# Grafana provisioning
apiVersion: 1
providers:
  - name: 'OpenDevin'
    folder: 'OpenDevin'
    type: file
    options:
      path: /var/lib