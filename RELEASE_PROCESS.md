# Release Process - Timestamp Versioning

This document outlines the release process using timestamp-based versioning for sprint releases.

## Versioning Strategy

We use timestamp-based versioning with the format: `YYYY.MM.DD.HHMM`

### Examples:
- `2024.10.22.1730` - Released on Oct 22, 2024 at 17:30
- `2024.11.05.0945` - Released on Nov 5, 2024 at 09:45

### Tag Formats:
- **Sprint releases**: `sprint-2024.10.22.1730`
- **Hotfixes**: `hotfix-2024.10.22.1730`
- **Major releases**: `release-2024.10.22.1730`

## Quick Release Commands

### Sprint Release (End of Sprint)
```bash
# Quick sprint release
./scripts/sprint-release.sh

# Or with Python script directly
poetry run python  scripts/release_sprint.py --type sprint
```

### Hotfix Release (Emergency fixes)
```bash
# Quick hotfix release
./scripts/hotfix-release.sh

# Or with Python script directly
poetry run python scripts/release_sprint.py --type hotfix
```

### Major Release
```bash
poetry run python scripts/release_sprint.py --type release
```

## Advanced Usage

### Dry Run (See what would happen)
```bash
python3 scripts/release_sprint.py --dry-run --type sprint
```

### Local Only (Don't push to remote)
```bash
python3 scripts/release_sprint.py --type sprint --no-push
```

## What the Release Script Does

1. **Checks Git Status**: Ensures working directory is clean
2. **Generates Timestamp Version**: Creates version like `2024.10.22.1730`
3. **Updates pyproject.toml**: Updates the version field
4. **Commits Changes**: Commits the version update
5. **Creates Git Tag**: Creates annotated tag with release info
6. **Pushes Everything**: Pushes commits and tags to remote

## Sprint Workflow

### At the End of Each Sprint:

1. **Ensure all work is committed and merged**
2. **Switch to main/develop branch**
3. **Run sprint release**:
   ```bash
   git checkout main
   git pull origin main
   ./scripts/sprint-release.sh
   ```

### For Emergency Hotfixes:

1. **Create hotfix branch** (optional)
2. **Make the fix and commit**
3. **Run hotfix release**:
   ```bash
   ./scripts/hotfix-release.sh
   ```

## Viewing Releases

### List All Tags
```bash
git tag -l
```

### List Recent Tags (Sorted)
```bash
git tag -l --sort=-version:refname | head -10
```

### View Tag Details
```bash
git show sprint-2024.10.22.1730
```

### List Tags by Pattern
```bash
# Sprint releases only
git tag -l "sprint-*"

# Hotfixes only
git tag -l "hotfix-*"

# This month's releases
git tag -l "*2024.10.*"
```

## Release Notes

After each sprint release, consider:

1. **Update CHANGELOG.md** with features and fixes
2. **Create GitHub Release** with release notes
3. **Notify team** of the new release
4. **Deploy to staging/production** if applicable

## Troubleshooting

### Working Directory Not Clean
```bash
# Check what's uncommitted
git status

# Commit or stash changes
git add .
git commit -m "Pre-release cleanup"
```

### Tag Already Exists
```bash
# Delete local tag
git tag -d sprint-2024.10.22.1730

# Delete remote tag
git push origin --delete sprint-2024.10.22.1730
```

### Failed Push
```bash
# Check remote connection
git remote -v

# Force push if needed (be careful!)
git push origin main --force-with-lease
```

## Benefits of Timestamp Versioning

- **Chronological**: Easy to see when releases were made
- **Unique**: No conflicts or confusion about versions
- **Sortable**: Natural sorting works correctly
- **Meaningful**: Version tells you exactly when it was released
- **Sprint-Friendly**: Perfect for regular sprint releases
