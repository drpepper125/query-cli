import boto3
import botocore
import json
from typing import List, Dict, Any


def get_ec2_instances(session: boto3.Session, region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """
    Get all Ec2 instnaces from a region
    """
    try:
        ec2_client = session.client('ec2', region_name=region)
        # Use paginator to get all EC2 instances in the region
        instances = []
        paginator = ec2_client.get_paginator('describe_instances')
        for page in paginator.paginate():
            for reservation in page.get('Reservations', []):
                for instance in reservation.get('Instances', []):
                    instances.append(instance)
        
        return instances
    except Exception as e:
        print(f'Error getting Ec2 instances: {e}')
        return []

if __name__ == "__main__":
    session = aws_helper.create_mgmt_session(env, account_id)
    ec2 = get_ec2.get_ec2_instances(session)
    print(ec2)