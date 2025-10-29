
## How to use it

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


# Or use a different port
poetry run uvicorn pecha_api.app:api --reload --port 8001
