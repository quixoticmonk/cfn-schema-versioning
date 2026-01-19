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
    
    # Load existing removed schemas
    removed_file = Path('removed_schemas.json')
    if removed_file.exists():
        with open(removed_file) as f:
            removed_schemas = json.load(f)
    else:
        removed_schemas = {}
    
    current_time = datetime.now().isoformat()
    
    # Track current AWS resource types to detect removals
    current_types = set()
    
    # Get all AWS resource types
    paginator = cfn.get_paginator('list_types')
    processed_count = 0
    
    for page in paginator.paginate(Visibility='PUBLIC', Type='RESOURCE'):
        for type_info in page['TypeSummaries']:
            type_name = type_info['TypeName']
            
            # Only process AWS resource types
            if not type_name.startswith('AWS::'):
                continue
            
            current_types.add(type_name)
                
            filename = type_name.replace('::', '--') + '.json'
            
            try:
                response = cfn.describe_type(Type='RESOURCE', TypeName=type_name)
                schema = json.loads(response['Schema'])
                
                # Extract additional metadata if available
                type_metadata = {
                    'time_created': response.get('TimeCreated'),
                    'deprecation_status': response.get('DeprecatedStatus')
                }
                
                # Check if schema changed
                schema_file = schemas_dir / filename
                schema_changed = True
                
                if schema_file.exists():
                    with open(schema_file) as f:
                        existing_schema = json.load(f)
                    schema_changed = existing_schema != schema
                
                # Save schema file
                with open(schema_file, 'w') as f:
                    json.dump(schema, f, indent=2, sort_keys=True)
                
                # Update version metadata
                if type_name not in versions:
                    versions[type_name] = {
                        'first_seen': current_time,
                        'last_updated': current_time,
                        **{k: v.isoformat() if hasattr(v, 'isoformat') else v 
                           for k, v in type_metadata.items() if v is not None}
                    }
                elif schema_changed:
                    versions[type_name]['last_updated'] = current_time
                
                # Always update AWS metadata if it exists (it might change independently of schema)
                for k, v in type_metadata.items():
                    if v is not None:
                        versions[type_name][k] = v.isoformat() if hasattr(v, 'isoformat') else v
                
                processed_count += 1
                if processed_count % 100 == 0:
                    print(f"Processed {processed_count} schemas...")
                
            except Exception as e:
                print(f"Error with {type_name}: {e}")
                continue
    
    # Check for removed schemas
    for type_name in list(versions.keys()):
        if type_name not in current_types:
            removed_schemas[type_name] = {
                **versions[type_name],
                'removed_date': current_time
            }
            del versions[type_name]
            print(f"Schema removed: {type_name}")
    
    # Save version metadata and removed schemas
    with open(version_file, 'w') as f:
        json.dump(versions, f, indent=2, sort_keys=True)
    
    with open(removed_file, 'w') as f:
        json.dump(removed_schemas, f, indent=2, sort_keys=True)

if __name__ == "__main__":
    main()
