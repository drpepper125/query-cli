#!/usr/bin/env python3
"""
AWS CLI Application - Main entry point.
This is the main CLI application that orchestrates AWS service queries.
"""

import argparse
import logging
import sys
from typing import Optional

# Import our AWS service modules
from aws_common import create_aws_session, get_available_regions
from get_certs import main as get_certificates
from get_ec2 import get_ec2_instances
from get_lb import get_load_balancers, format_load_balancers_for_table


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )


def list_services() -> None:
    """List available AWS services."""
    services = [
        "certificates - Get SSL/TLS certificate information",
        "ec2 - Get EC2 instance information", 
        "load-balancers - Get load balancer information",
        "regions - List available AWS regions"
    ]
    
    print("\nAvailable AWS services:")
    for service in services:
        print(f"  - {service}")


def get_certificates_command(region: str, profile: Optional[str] = None) -> None:
    """Execute certificate analysis."""
    try:
        logging.info(f"Starting certificate analysis for region: {region}")
        result = get_certificates()
        
        if result:
            print(f"\nCertificate Analysis Complete!")
            print(f"Total certificates: {result['summary']['total_certificates']}")
            print(f"Status breakdown: {result['summary']['status_counts']}")
            
            if result['summary']['expired_count'] > 0:
                print(f"⚠️  {result['summary']['expired_count']} expired certificates found!")
            if result['summary']['approaching_count'] > 0:
                print(f"⚠️  {result['summary']['approaching_count']} certificates approaching expiration!")
        else:
            print("No certificate data retrieved.")
            
    except Exception as e:
        logging.error(f"Error in certificate analysis: {str(e)}")
        sys.exit(1)


def get_ec2_command(region: str, profile: Optional[str] = None) -> None:
    """Execute EC2 instance analysis."""
    try:
        logging.info(f"Starting EC2 analysis for region: {region}")
        session = create_aws_session(profile=profile, region=region)
        instances = get_ec2_instances(session, region)
        
        if instances:
            print(f"\nEC2 Analysis Complete!")
            print(f"Total instances found: {len(instances)}")
            
            # Count by state
            state_counts = {}
            for instance in instances:
                state = instance.get('State', {}).get('Name', 'unknown')
                state_counts[state] = state_counts.get(state, 0) + 1
            
            print(f"Instance states: {state_counts}")
        else:
            print("No EC2 instances found.")
            
    except Exception as e:
        logging.error(f"Error in EC2 analysis: {str(e)}")
        sys.exit(1)


def get_load_balancers_command(region: str, profile: Optional[str] = None) -> None:
    """Execute load balancer analysis."""
    try:
        logging.info(f"Starting load balancer analysis for region: {region}")
        session = create_aws_session(profile=profile, region=region)
        load_balancers = get_load_balancers(session, region)
        
        if load_balancers:
            table_data = format_load_balancers_for_table(load_balancers)
            print(f"\nLoad Balancer Analysis Complete!")
            print(f"Total load balancers found: {len(table_data)}")
            
            # Count by type
            type_counts = {}
            for lb in table_data:
                lb_type = lb['Type']
                type_counts[lb_type] = type_counts.get(lb_type, 0) + 1
            
            print(f"Load balancer types: {type_counts}")
        else:
            print("No load balancers found.")
            
    except Exception as e:
        logging.error(f"Error in load balancer analysis: {str(e)}")
        sys.exit(1)


def list_regions_command() -> None:
    """List available AWS regions."""
    try:
        regions = get_available_regions()
        print(f"\nAvailable AWS regions ({len(regions)} total):")
        for region in sorted(regions):
            print(f"  - {region}")
    except Exception as e:
        logging.error(f"Error getting regions: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AWS CLI Application - Query AWS services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py certificates --region us-west-2
  python main.py ec2 --region us-east-1 --profile myprofile
  python main.py load-balancers --region eu-west-1
  python main.py regions
        """
    )
    
    parser.add_argument(
        'service',
        choices=['certificates', 'ec2', 'load-balancers', 'regions'],
        help='AWS service to query'
    )
    
    parser.add_argument(
        '--region', '-r',
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    
    parser.add_argument(
        '--profile', '-p',
        help='AWS profile to use'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--list-services',
        action='store_true',
        help='List available services and exit'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Handle list services
    if args.list_services:
        list_services()
        return
    
    # Execute service-specific commands
    if args.service == 'certificates':
        get_certificates_command(args.region, args.profile)
    elif args.service == 'ec2':
        get_ec2_command(args.region, args.profile)
    elif args.service == 'load-balancers':
        get_load_balancers_command(args.region, args.profile)
    elif args.service == 'regions':
        list_regions_command()


if __name__ == "__main__":
    main()
