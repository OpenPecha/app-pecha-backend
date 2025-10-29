# Development Scripts

This folder contains utility scripts for local development.

## Scripts

### 🚀 `start_dev.sh` (Recommended)
Main development server with auto-reload and proper exclusions.

```bash
./dev/start_dev.sh
```

**Features:**
- Auto-reload on file changes (fast)
- Excludes database directories from watching
- Uses Poetry virtual environment

---

### 🔧 `fix_permissions.sh`
Fixes database directory permissions for file watching.

```bash
./dev/fix_permissions.sh
```

**When to use:**
- First time setup
- After database reset
- When you get permission errors

**What it does:**
- Sets proper permissions on `local_setup/data/` directories
- Changes ownership to current user
- Requires sudo password

---

### 🐌 `start_dev_statreload.sh`
Alternative server with polling-based reload (slower but more reliable).

```bash
./dev/start_dev_statreload.sh
```

**When to use:**
- If `start_dev.sh` has file watching issues
- If you can't run `fix_permissions.sh`
- When you don't have sudo access

**Trade-off:**
- Slower change detection (2 second polling)
- No permission issues

---

### 🛑 `start_dev_no_reload.sh`
Server without auto-reload.

```bash
./dev/start_dev_no_reload.sh
```

**When to use:**
- Production-like testing
- When you want to manually control restarts
- Debugging reload-related issues

---

## Quick Start

1. **First time setup:**
   ```bash
   cd /path/to/app-pecha-backend
   ./dev/fix_permissions.sh
   ```

2. **Start development server:**
   ```bash
   ./dev/start_dev.sh
   ```

3. **Access the API:**
   - API: http://127.0.0.1:8000
   - Docs: http://127.0.0.1:8000/docs

---

## Troubleshooting

### Permission Errors
```
PermissionError: Permission denied (os error 13)
```
**Solution:** Run `./dev/fix_permissions.sh`

### Port Already in Use
```
ERROR: [Errno 98] Address already in use
```
**Solution:** 
```bash
# Kill existing server
pkill -f "uvicorn pecha_api.app:api"

# Or use a different port
poetry run uvicorn pecha_api.app:api --reload --port 8001
```

### Auto-reload Not Working
**Solution:** Try `./dev/start_dev_statreload.sh` instead
