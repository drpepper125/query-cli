"""
Common AWS utilities and shared functionality.
This module contains shared AWS operations to avoid circular imports.
"""

import boto3
import logging
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError


def create_aws_session(profile: Optional[str] = None, region: str = 'us-east-1') -> boto3.Session:
    """
    Create an AWS session with optional profile and region.
    
    Args:
        profile (str, optional): AWS profile name
        region (str): AWS region
        
    Returns:
        boto3.Session: Configured AWS session
    """
    try:
        if profile:
            session = boto3.Session(profile_name=profile)
        else:
            session = boto3.Session()
        
        # Set default region
        session._region = region
        return session
        
    except NoCredentialsError:
        logging.error("AWS credentials not found. Please configure your credentials.")
        raise
    except Exception as e:
        logging.error(f"Error creating AWS session: {str(e)}")
        raise


def get_available_regions(service: str = 'ec2') -> list:
    """
    Get list of available AWS regions for a service.
    
    Args:
        service (str): AWS service name
        
    Returns:
        list: List of region names
    """
    try:
        session = boto3.Session()
        return session.get_available_regions(service)
    except Exception as e:
        logging.error(f"Error getting available regions: {str(e)}")
        return []


def handle_aws_error(error: ClientError, operation: str) -> None:
    """
    Handle AWS client errors with appropriate logging.
    
    Args:
        error (ClientError): The AWS client error
        operation (str): Description of the operation that failed
    """
    error_code = error.response['Error']['Code']
    error_message = error.response['Error']['Message']
    
    if error_code == 'UnauthorizedOperation':
        logging.error(f"Unauthorized to perform {operation}. Check your IAM permissions.")
    elif error_code == 'InvalidParameterValue':
        logging.error(f"Invalid parameter for {operation}: {error_message}")
    elif error_code == 'ThrottlingException':
        logging.warning(f"Rate limited for {operation}. Consider adding delays between requests.")
    else:
        logging.error(f"AWS Error during {operation}: {error_code} - {error_message}")


def format_aws_response(data: Any, indent: int = 2) -> str:
    """
    Format AWS response data as JSON string.
    
    Args:
        data: Data to format
        indent (int): JSON indentation
        
    Returns:
        str: Formatted JSON string
    """
    import json
    return json.dumps(data, indent=indent, default=str)
