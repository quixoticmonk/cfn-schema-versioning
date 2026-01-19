# AWS CloudFormation Schema Version Tracker

This repository tracks AWS CloudFormation resource type schema changes using git diffs to determine actual update dates. This is an approximation of when schemas would have changed.

## What this provides

1. **Schema versioning**: Preserves every version of each CloudFormation schema in git history
2. **Change traceability**: Git diffs show exactly what changed between schema versions
3. **Timeline tracking**: Metadata tracks when changes were detected (approximation of AWS release dates)

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

This tracks when schema changes are **detected** through daily monitoring, providing a timeline of schema evolution relative to your monitoring schedule.
