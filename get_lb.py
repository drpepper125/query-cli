"""
AWS Load Balancer utilities.
"""

import boto3
import logging
from typing import List, Dict, Any, Optional
from botocore.exceptions import ClientError
from aws_common import create_aws_session, handle_aws_error


def get_load_balancers(session: boto3.Session, region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """
    Get all load balancers (ALB, NLB, CLB) from a region.
    
    Args:
        session (boto3.Session): AWS session
        region (str): AWS region
        
    Returns:
        List[Dict]: List of load balancer information
    """
    all_load_balancers = []
    
    # Get Application Load Balancers (ALB)
    try:
        elbv2_client = session.client('elbv2', region_name=region)
        alb_response = elbv2_client.describe_load_balancers()
        albs = alb_response.get('LoadBalancers', [])
        
        for alb in albs:
            alb['Type'] = 'ALB'
            alb['Service'] = 'elbv2'
            all_load_balancers.append(alb)
            
        logging.info(f"Found {len(albs)} Application Load Balancers")
        
    except ClientError as e:
        handle_aws_error(e, "describe ALBs")
    except Exception as e:
        logging.error(f"Error getting ALBs: {str(e)}")
    
    # Get Classic Load Balancers (CLB)
    try:
        elb_client = session.client('elb', region_name=region)
        clb_response = elb_client.describe_load_balancers()
        clbs = clb_response.get('LoadBalancerDescriptions', [])
        
        for clb in clbs:
            clb['Type'] = 'CLB'
            clb['Service'] = 'elb'
            all_load_balancers.append(clb)
            
        logging.info(f"Found {len(clbs)} Classic Load Balancers")
        
    except ClientError as e:
        handle_aws_error(e, "describe CLBs")
    except Exception as e:
        logging.error(f"Error getting CLBs: {str(e)}")
    
    return all_load_balancers


def get_load_balancer_details(session: boto3.Session, lb_arn: str, lb_type: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """
    Get detailed information for a specific load balancer.
    
    Args:
        session (boto3.Session): AWS session
        lb_arn (str): Load balancer ARN or name
        lb_type (str): Type of load balancer (ALB, CLB)
        region (str): AWS region
        
    Returns:
        Dict: Load balancer details
    """
    try:
        if lb_type == 'ALB':
            elbv2_client = session.client('elbv2', region_name=region)
            response = elbv2_client.describe_load_balancers(LoadBalancerArns=[lb_arn])
            return response['LoadBalancers'][0] if response['LoadBalancers'] else {}
        elif lb_type == 'CLB':
            elb_client = session.client('elb', region_name=region)
            response = elb_client.describe_load_balancers(LoadBalancerNames=[lb_arn])
            return response['LoadBalancerDescriptions'][0] if response['LoadBalancerDescriptions'] else {}
        else:
            logging.warning(f"Unknown load balancer type: {lb_type}")
            return {}
            
    except ClientError as e:
        handle_aws_error(e, f"describe {lb_type} details")
        return {}
    except Exception as e:
        logging.error(f"Error getting {lb_type} details: {str(e)}")
        return {}


def format_load_balancers_for_table(load_balancers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format load balancer data for table display.
    
    Args:
        load_balancers (List): List of load balancer data
        
    Returns:
        List[Dict]: Formatted load balancer data
    """
    table_data = []
    
    for lb in load_balancers:
        if lb.get('Type') == 'ALB':
            row = {
                'Name': lb.get('LoadBalancerName', 'N/A'),
                'Type': 'ALB',
                'ARN': lb.get('LoadBalancerArn', 'N/A'),
                'DNS Name': lb.get('DNSName', 'N/A'),
                'State': lb.get('State', {}).get('Code', 'N/A'),
                'Scheme': lb.get('Scheme', 'N/A'),
                'VPC ID': lb.get('VpcId', 'N/A'),
                'Created Time': lb.get('CreatedTime', 'N/A')
            }
        else:  # CLB
            row = {
                'Name': lb.get('LoadBalancerName', 'N/A'),
                'Type': 'CLB',
                'ARN': 'N/A',  # CLBs don't have ARNs
                'DNS Name': lb.get('DNSName', 'N/A'),
                'State': 'N/A',  # CLBs don't have state in the same format
                'Scheme': lb.get('Scheme', 'N/A'),
                'VPC ID': lb.get('VPCId', 'N/A'),
                'Created Time': lb.get('CreatedTime', 'N/A')
            }
        
        table_data.append(row)
    
    return table_data


def main():
    """
    Main function to get load balancer information.
    """
    region = 'us-east-1'
    
    logging.info("Starting load balancer analysis...")
    
    # Create AWS session
    session = create_aws_session(region=region)
    
    # Get all load balancers
    load_balancers = get_load_balancers(session, region)
    
    if not load_balancers:
        logging.warning("No load balancers found or error occurred")
        return
    
    # Format for display
    table_data = format_load_balancers_for_table(load_balancers)
    
    # Display results
    logging.info(f"\nLoad Balancer Analysis Results:")
    logging.info(f"Total load balancers found: {len(table_data)}")
    
    # Count by type
    type_counts = {}
    for lb in table_data:
        lb_type = lb['Type']
        type_counts[lb_type] = type_counts.get(lb_type, 0) + 1
    
    logging.info(f"Type breakdown: {type_counts}")
    
    return {
        'load_balancers': load_balancers,
        'table_data': table_data,
        'summary': {
            'total_load_balancers': len(table_data),
            'type_counts': type_counts
        }
    }


if __name__ == "__main__":
    result = main()