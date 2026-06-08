#!/usr/bin/env bash
# =============================================================================
# Hermesclaw Validation Script (Unix/macOS)
# =============================================================================
# Validates the Hermesclaw OpenClaw+Hermes Agent integration on Linux/macOS.
# Complement to validate.ps1 for Windows — provides parity for Unix platforms.
#
# Usage: ./validate.sh [--verbose] [--skip-docker]
#   --verbose    Show detailed output
#   --skip-docker Skip Docker validation (for environments without Docker)
# =============================================================================

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
VERBOSE=false
SKIP_DOCKER=false
ERRORS=0
WARNINGS=0

# Project root (script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

log_info()  { echo -e "${BLUE}[INFO]${NC}  $*"; }
log_pass()  { echo -e "${GREEN}[PASS]${NC}  $*"; }
log_fail()  { echo -e "${RED}[FAIL]${NC}  $*"; ((ERRORS++)); }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $*"; ((WARNINGS++)); }

verbose()    { if [[ "$VERBOSE" == "true" ]]; then echo -e "         $*" >&2; fi; }

section()    { echo ""; echo "━━━ $1 ━━━"; }

# ---------------------------------------------------------------------------
# Parse flags
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose) VERBOSE=true; shift ;;
        --skip-docker) SKIP_DOCKER=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# Check: Git available
# ---------------------------------------------------------------------------
check_git() {
    section "Git"
    if command -v git >/dev/null 2>&1; then
        local git_ver
        git_ver=$(git --version)
        log_pass "$git_ver"
        verbose "Found at: $(command -v git)"
    else
        log_fail "Git not found — required for version control"
    fi
}

# ---------------------------------------------------------------------------
# Check: Node.js and npm
# ---------------------------------------------------------------------------
check_node() {
    section "Node.js & npm"
    if command -v node >/dev/null 2>&1; then
        local node_ver
        node_ver=$(node --version)
        log_pass "Node.js: $node_ver"

        # Check for package.json
        local pkg_json="$PROJECT_ROOT/packages/openclaw-hermes-adapter/package.json"
        if [[ -f "$pkg_json" ]]; then
            log_pass "package.json found"
            verbose "Path: $pkg_json"
        else
            log_warn "package.json not found at $pkg_json"
        fi

        # Check npm
        if command -v npm >/dev/null 2>&1; then
            local npm_ver
            npm_ver=$(npm --version)
            log_pass "npm: $npm_ver"
        else
            log_fail "npm not found"
        fi

        # Node version check (>= 18)
        local node_major
        node_major=$(node --version | sed 's/v\([0-9]*\).*/\1/')
        if (( node_major >= 18 )); then
            log_pass "Node.js version OK (>= 18)"
        else
            log_fail "Node.js version too old (need >= 18, got $node_major)"
        fi
    else
        log_fail "Node.js not found — required for TypeScript adapter"
    fi
}

# ---------------------------------------------------------------------------
# Check: Python
# ---------------------------------------------------------------------------
check_python() {
    section "Python"
    if command -v python3 >/dev/null 2>&1; then
        local py_ver
        py_ver=$(python3 --version)
        log_pass "$py_ver"

        # Check pip
        if command -v pip3 >/dev/null 2>&1; then
            local pip_ver
            pip_ver=$(pip3 --version | awk '{print $2}')
            log_pass "pip3: $pip_ver"
        else
            log_warn "pip3 not found — Python packages can't be installed"
        fi

        # Python version check (>= 3.10)
        local py_major py_minor
        py_major=$(python3 --version | awk '{print $2}' | cut -d. -f1)
        py_minor=$(python3 --version | awk '{print $2}' | cut -d. -f2)
        if (( py_major > 3 )) || (( py_major == 3 && py_minor >= 10 )); then
            log_pass "Python version OK (>= 3.10)"
        else
            log_fail "Python version too old (need >= 3.10)"
        fi
    else
        log_fail "Python 3 not found — required for Hermes bridge"
    fi
}

# ---------------------------------------------------------------------------
# Check: Docker
# ---------------------------------------------------------------------------
check_docker() {
    if [[ "$SKIP_DOCKER" == "true" ]]; then
        section "Docker (skipped by --skip-docker)"
        log_warn "Docker checks skipped"
        return
    fi

    section "Docker & Docker Compose"
    if command -v docker >/dev/null 2>&1; then
        local docker_ver
        docker_ver=$(docker --version)
        log_pass "$docker_ver"

        # Check docker-compose
        if command -v docker-compose >/dev/null 2>&1; then
            local dc_ver
            dc_ver=$(docker-compose --version)
            log_pass "docker-compose: $dc_ver"
        elif docker compose version >/dev/null 2>&1; then
            local dc_ver
            dc_ver=$(docker compose version)
            log_pass "docker compose: $dc_ver"
        else
            log_warn "docker-compose not found (optional)"
        fi

        # Check docker daemon is running
        if docker info >/dev/null 2>&1; then
            log_pass "Docker daemon is running"
        else
            log_warn "Docker daemon is not running (start Docker app or dockerd)"
        fi

        # Check docker-compose.yml exists
        local compose_file="$PROJECT_ROOT/services/hermes-bridge/docker-compose.yml"
        if [[ -f "$compose_file" ]]; then
            log_pass "docker-compose.yml found"
            verbose "Path: $compose_file"
        else
            log_warn "docker-compose.yml not found at $compose_file"
        fi
    else
        log_warn "Docker not found (optional for local development)"
    fi
}

# ---------------------------------------------------------------------------
# Check: Git submodules
# ---------------------------------------------------------------------------
check_submodules() {
    section "Git Submodules"
    local submodules_file="$PROJECT_ROOT/.gitmodules"
    if [[ -f "$submodules_file" ]]; then
        log_pass ".gitmodules found"
        verbose "Checking submodule status..."
        # Check if submodules are initialized (non-empty .git files exist)
        local openclaw_submod="$PROJECT_ROOT/.git/modules/openclaw"
        local hermes_submod="$PROJECT_ROOT/.git/modules/hermes-agent"
        if [[ -d "$openclaw_submod" ]] || git submodule status 2>/dev/null | grep -q "^[+- ]"; then
            log_pass "Git submodules appear to be initialized"
            git submodule status 2>/dev/null | head -5 | while read -r line; do
                verbose "  $line"
            done
        else
            log_warn "Git submodules not initialized — run: git submodule update --init --recursive"
        fi
    else
        log_info "No .gitmodules file (submodules not used in this project)"
    fi
}

# ---------------------------------------------------------------------------
# Check: TypeScript compilation
# ---------------------------------------------------------------------------
check_typescript() {
    section "TypeScript / npm packages"
    local adapter_dir="$PROJECT_ROOT/packages/openclaw-hermes-adapter"

    if [[ -d "$adapter_dir" ]]; then
        if [[ -f "$adapter_dir/package.json" ]]; then
            log_pass "openclaw-hermes-adapter package.json found"

            # Check if node_modules exists
            if [[ -d "$adapter_dir/node_modules" ]]; then
                log_pass "node_modules installed"
            else
                log_warn "node_modules not found — run: npm install"
            fi

            # Try TypeScript type check (if tsc available)
            if command -v npx >/dev/null 2>&1; then
                if [[ -f "$adapter_dir/tsconfig.json" ]]; then
                    verbose "Running TypeScript type check..."
                    if npx tsc --noEmit --project "$adapter_dir" >/dev/null 2>&1; then
                        log_pass "TypeScript: no type errors"
                    else
                        log_warn "TypeScript has type errors (run: npx tsc --noEmit to see details)"
                    fi
                fi
            fi
        else
            log_warn "openclaw-hermes-adapter has no package.json"
        fi
    else
        log_warn "packages/openclaw-hermes-adapter directory not found"
    fi
}

# ---------------------------------------------------------------------------
# Check: Python bridge import
# ---------------------------------------------------------------------------
check_python_bridge() {
    section "Python Bridge (Hermes)"
    local bridge_dir="$PROJECT_ROOT/services/hermes-bridge"

    if [[ -d "$bridge_dir" ]]; then
        log_pass "hermes-bridge directory found"

        # Check for main Python files
        if [[ -f "$bridge_dir/main.py" ]] || [[ -f "$bridge_dir/bridge.py" ]]; then
            log_pass "Bridge entry point found"
            local entry
            entry=$(ls "$bridge_dir"/{main,bridge}.py 2>/dev/null | head -1)
            verbose "Entry: $entry"
        else
            log_warn "No main.py or bridge.py found"
        fi

        # Try importing the bridge
        if command -v python3 >/dev/null 2>&1; then
            if python3 -c "import fastapi" 2>/dev/null; then
                log_pass "FastAPI available"
            else
                log_warn "FastAPI not installed (bridge requires: pip install fastapi uvicorn)"
            fi
        fi
    else
        log_warn "services/hermes-bridge directory not found"
    fi
}

# ---------------------------------------------------------------------------
# Check: OpenClaw CLI
# ---------------------------------------------------------------------------
check_openclaw() {
    section "OpenClaw CLI"
    if command -v openclaw >/dev/null 2>&1; then
        local oc_ver
        oc_ver=$(openclaw --version 2>&1 | head -1)
        log_pass "OpenClaw CLI: $oc_ver"
    else
        log_warn "openclaw CLI not found in PATH (required for backend)"
    fi
}

# ---------------------------------------------------------------------------
# Check: Port availability
# ---------------------------------------------------------------------------
check_ports() {
    section "Port Availability"
    # Common ports used by Hermesclaw
    local ports=("18789" "8000" "3000")
    local port_names=("OpenClaw default" "Hermes bridge" "TypeScript dev")

    for i in "${!ports[@]}"; do
        local port="${ports[$i]}"
        local name="${port_names[$i]}"
        # Check if port is in use (macOS and Linux compatible)
        if lsof -i ":$port" >/dev/null 2>&1 || netstat -an 2>/dev/null | grep -q ":$port " || ss -an 2>/dev/null | grep -q ":$port "; then
            verbose "$port ($name): in use"
        else
            log_pass "Port $port ($name): available"
        fi
    done
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
summary() {
    section "Summary"
    if (( ERRORS == 0 )); then
        log_pass "All critical checks passed!"
    else
        log_fail "$ERRORS critical check(s) failed"
    fi

    if (( WARNINGS > 0 )); then
        log_warn "$WARNINGS warning(s)"
    fi

    echo ""
    if (( ERRORS == 0 )); then
        echo -e "${GREEN}✅ Hermesclaw validation complete — ready to develop!${NC}"
        echo ""
        echo "Next steps:"
        echo "  1. cd packages/openclaw-hermes-adapter && npm install && npm run build"
        echo "  2. cd services/hermes-bridge && pip install -r requirements.txt"
        echo "  3. docker-compose up -d"
        echo "  4. openclaw start"
    else
        echo -e "${RED}❌ Fix the failed checks before continuing${NC}"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Hermesclaw Validation (Unix/macOS)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Project: $PROJECT_ROOT"
echo "  Verbose: $VERBOSE | Skip Docker: $SKIP_DOCKER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

check_git
check_node
check_python
check_docker
check_submodules
check_typescript
check_python_bridge
check_openclaw
check_ports
summary