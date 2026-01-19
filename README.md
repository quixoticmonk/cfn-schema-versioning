# AWS CloudFormation Schema Version Tracker

This repository tracks AWS CloudFormation resource type schema changes using git diffs to determine actual update dates.

## How it works

1. **Daily fetch**: GitHub Actions runs daily to fetch all AWS resource type schemas
2. **Diff detection**: Uses `git diff` to detect actual schema changes
3. **Version tracking**: Only updates timestamps when schemas actually change
4. **Git history**: Full change history preserved in git commits

## Files

- `schemas/`: Individual schema files (AWS--S3--Bucket.json, etc.)
- `version_metadata.json`: Last update timestamp (only updated when changes detected)
- `fetch_schemas.py`: Script to fetch all schemas from AWS
- `.github/workflows/schema-tracker.yml`: GitHub Actions workflow

## Usage

The workflow automatically:
- Fetches all AWS resource type schemas
- Compares with previous versions using git diff
- Only commits and updates timestamps when actual changes are found
- Preserves full history of schema evolution

This gives you accurate schema version dates based on actual content changes, not arbitrary API timestamps.
