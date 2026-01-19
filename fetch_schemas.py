#!/usr/bin/env python3
import json
import boto3
from datetime import datetime
from pathlib import Path

def main():
    cfn = boto3.client('cloudformation')
    schemas_dir = Path('schemas')
    schemas_dir.mkdir(exist_ok=True)
    
    # Load existing version metadata
    version_file = Path('version_metadata.json')
    if version_file.exists():
        with open(version_file) as f:
            versions = json.load(f)
    else:
        versions = {}
    
    current_time = datetime.now().isoformat()
    
    # Get all AWS resource types
    paginator = cfn.get_paginator('list_types')
    processed_count = 0
    
    for page in paginator.paginate(Visibility='PUBLIC', Type='RESOURCE'):
        for type_info in page['TypeSummaries']:
            type_name = type_info['TypeName']
            filename = type_name.replace('::', '--') + '.json'
            
            try:
                response = cfn.describe_type(Type='RESOURCE', TypeName=type_name)
                schema = json.loads(response['Schema'])
                
                # Save schema file
                with open(schemas_dir / filename, 'w') as f:
                    json.dump(schema, f, indent=2, sort_keys=True)
                
                # Initialize version metadata if not exists
                if type_name not in versions:
                    versions[type_name] = {
                        'first_seen': current_time,
                        'last_updated': current_time
                    }
                
                processed_count += 1
                if processed_count % 100 == 0:
                    print(f"Processed {processed_count} schemas...")
                
            except Exception as e:
                print(f"Error with {type_name}: {e}")
                continue
    
    # Save version metadata
    with open(version_file, 'w') as f:
        json.dump(versions, f, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
