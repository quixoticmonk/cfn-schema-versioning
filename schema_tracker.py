#!/usr/bin/env python3
"""
AWS CloudFormation Schema Version Tracker

Fetches all AWS resource type schemas, stores them in git, and tracks
actual schema changes to determine version update dates.
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
import boto3

class SchemaTracker:
    def __init__(self, repo_path="./cfn-schemas"):
        self.repo_path = Path(repo_path)
        self.cfn = boto3.client('cloudformation')
        
    def init_repo(self):
        """Initialize git repository for schema tracking"""
        if not self.repo_path.exists():
            self.repo_path.mkdir(parents=True)
            os.chdir(self.repo_path)
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'config', 'user.email', 'schema-tracker@example.com'], check=True)
            subprocess.run(['git', 'config', 'user.name', 'Schema Tracker'], check=True)
        else:
            os.chdir(self.repo_path)
    
    def fetch_all_schemas(self):
        """Fetch all AWS resource type schemas"""
        print("Fetching all AWS resource types...")
        
        # Get all resource types
        paginator = self.cfn.get_paginator('list_types')
        types = []
        
        for page in paginator.paginate(Visibility='PUBLIC', Type='RESOURCE'):
            types.extend(page['TypeSummaries'])
        
        print(f"Found {len(types)} resource types")
        
        # Fetch schema for each type
        schemas = {}
        for i, type_info in enumerate(types, 1):
            type_name = type_info['TypeName']
            print(f"[{i}/{len(types)}] Fetching {type_name}")
            
            try:
                response = self.cfn.describe_type(
                    Type='RESOURCE',
                    TypeName=type_name
                )
                
                schema_data = {
                    'TypeName': type_name,
                    'TimeCreated': response['TimeCreated'].isoformat(),
                    'Schema': json.loads(response['Schema'])
                }
                
                schemas[type_name] = schema_data
                
            except Exception as e:
                print(f"  Error fetching {type_name}: {e}")
                continue
        
        return schemas
    
    def save_schemas(self, schemas):
        """Save schemas to individual files"""
        schemas_dir = self.repo_path / "schemas"
        schemas_dir.mkdir(exist_ok=True)
        
        for type_name, schema_data in schemas.items():
            # Convert :: to -- for filename
            filename = type_name.replace('::', '--') + '.json'
            file_path = schemas_dir / filename
            
            with open(file_path, 'w') as f:
                json.dump(schema_data, f, indent=2, sort_keys=True)
    
    def commit_changes(self):
        """Commit any schema changes to git"""
        os.chdir(self.repo_path)
        
        # Add all changes
        subprocess.run(['git', 'add', '.'], check=True)
        
        # Check if there are changes to commit
        result = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True)
        
        if result.returncode != 0:  # There are changes
            timestamp = datetime.now().isoformat()
            subprocess.run([
                'git', 'commit', 
                '-m', f'Schema update: {timestamp}'
            ], check=True)
            print(f"Committed schema changes at {timestamp}")
            return True
        else:
            print("No schema changes detected")
            return False
    
    def get_schema_versions(self):
        """Get version history for all schemas based on git commits"""
        os.chdir(self.repo_path)
        
        versions = {}
        
        # Get all schema files
        schemas_dir = self.repo_path / "schemas"
        if not schemas_dir.exists():
            return versions
        
        for schema_file in schemas_dir.glob('*.json'):
            type_name = schema_file.stem.replace('--', '::')
            
            # Get git log for this file
            try:
                result = subprocess.run([
                    'git', 'log', '--format=%H|%ci', '--', str(schema_file)
                ], capture_output=True, text=True, check=True)
                
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        commit_hash, commit_date = line.split('|', 1)
                        commits.append({
                            'commit': commit_hash[:8],
                            'date': commit_date,
                            'timestamp': commit_date
                        })
                
                versions[type_name] = {
                    'latest_update': commits[0]['date'] if commits else None,
                    'total_updates': len(commits),
                    'history': commits[:5]  # Last 5 updates
                }
                
            except subprocess.CalledProcessError:
                versions[type_name] = {
                    'latest_update': None,
                    'total_updates': 0,
                    'history': []
                }
        
        return versions
    
    def run_update(self):
        """Main update process"""
        print("Starting schema update process...")
        
        self.init_repo()
        schemas = self.fetch_all_schemas()
        self.save_schemas(schemas)
        
        has_changes = self.commit_changes()
        
        if has_changes:
            print("Schema changes detected and committed!")
        
        return self.get_schema_versions()

def main():
    tracker = SchemaTracker()
    versions = tracker.run_update()
    
    # Show some examples
    print(f"\nVersion tracking for {len(versions)} resource types:")
    for type_name, version_info in list(versions.items())[:5]:
        print(f"  {type_name}: {version_info['latest_update']} ({version_info['total_updates']} updates)")

if __name__ == "__main__":
    main()
