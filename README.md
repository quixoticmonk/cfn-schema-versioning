# AWS CloudFormation Schema Version Tracker

This repository tracks AWS CloudFormation resource type schema changes using git diffs to determine actual update dates. This provides an approximation of when schemas changed based on twice-weekly monitoring.

## What this provides

1. **Schema versioning**: Preserves every version of each CloudFormation schema in git history
2. **Change traceability**: Git diffs show exactly what changed between schema versions  
3. **Timeline tracking**: Approximate metadata tracking of when changes were detected and AWS metadata
4. **AWS metadata**: Captures additional AWS-provided metadata like creation time and deprecation status
5. **Terraform AWSCC tracking**: Monitor schema changes that affect the Terraform AWS Cloud Control (AWSCC) provider

## How it works

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Actions Workflow                     │
│                 (Mondays & Wednesdays 6AM UTC)                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   fetch_schemas.py                              │
│  ┌─────────────────┐    ┌─────────────────┐                    │
│  │ Load existing   │    │ Load existing   │                    │
│  │ version_        │    │ removed_        │                    │
│  │ metadata.json   │    │ schemas.json    │                    │
│  └─────────────────┘    └─────────────────┘                    │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │        Fetch all AWS CloudFormation schemas                ││
│  │              (boto3 CloudFormation API)                    ││
│  └─────────────────────────────────────────────────────────────┘│
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  For each schema:                                           ││
│  │  • Compare with existing file                               ││
│  │  • Update schemas/ if changed                               ││
│  │  • Update metadata if new/changed                           ││
│  └─────────────────────────────────────────────────────────────┘│
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Check for removed schemas:                                 ││
│  │  • Compare current vs previous types                        ││
│  │  • Move removed to removed_schemas.json                     ││
│  │  • Remove from version_metadata.json                        ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Git Commit & Push                           │
│  • Only if schemas/ or metadata files changed                  │
│  • Timestamped commit message                                  │
│  • Preserves full history                                      │
└─────────────────────────────────────────────────────────────────┘
```

1. **Scheduled fetch**: GitHub Actions runs on Mondays and Wednesdays at 6 AM UTC to fetch all AWS resource type schemas
2. **Schema comparison**: Compares new schemas with existing files to detect actual changes
3. **Selective updates**: Only commits and updates timestamps when schemas actually change
4. **Metadata tracking**: Tracks both local detection time and AWS-provided metadata
5. **Git history**: Full change history preserved in git commits with timestamps

## Files

- `schemas/`: Individual schema files (AWS--S3--Bucket.json, etc.)
- `version_metadata.json`: Comprehensive metadata for active schemas
- `removed_schemas.json`: Metadata for schemas that are no longer available from AWS
- `fetch_schemas.py`: Main script to fetch all schemas from AWS and detect changes
- `schema_tracker.py`: Alternative implementation with git repository management
- `requirements.txt`: Python dependencies (boto3)
- `.github/workflows/schema-tracker.yml`: GitHub Actions workflow with AWS OIDC authentication

## Workflow Features

- **AWS OIDC authentication**: Uses role-based authentication instead of access keys
- **uv package manager**: Fast Python dependency installation
- **Change detection**: Only commits when actual schema changes are detected
- **Batch processing**: Processes schemas in batches with progress reporting
- **Error handling**: Continues processing even if individual schemas fail

## Version Metadata Structure

Each resource type in `version_metadata.json` includes:
- `first_seen`: When the schema was first detected by this tracking system (arbitrary for pre-existing schemas)
- `last_updated`: When the schema last changed (local detection)
- `time_created`: AWS-provided creation timestamp (authoritative creation date)
- `deprecation_status`: Current deprecation status

Note: AWS also provides `DefaultVersionId` in the API, but it returns null for public extensions like AWS resource types.

Each resource type in `removed_schemas.json` includes all the above fields plus:
- `removed_date`: When the schema was no longer available from AWS

## Usage

The workflow automatically runs twice weekly and can also be triggered manually via `workflow_dispatch`. It:
- Fetches all public AWS resource type schemas
- Compares with previous versions to detect changes
- Updates metadata only for changed schemas
- Commits changes with timestamped messages
- Preserves complete schema evolution history

This tracks when schema changes are **detected** through twice-weekly monitoring, providing a timeline of schema evolution relative to the monitoring schedule.
