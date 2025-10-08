import boto3 
import logging
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any
import json


logging.basicConfig(level=logging.INFO, stream=sys.stdout)


def get_all_certificates(region: str = 'us-east-1') -> List[Dict[str, Any]]:
    """
    Retrieve all certificates from AWS Certificate Manager.
    
    Args:
        region (str): AWS region to query
        
    Returns:
        List[Dict]: List of certificate summaries
    """
    try:
        acm_client = boto3.client('acm', region_name=region)
        
        # Get all certificates
        response = acm_client.list_certificates()
        certificates = response['CertificateSummaryList']
        
        logging.info(f"Found {len(certificates)} certificates in region {region}")
        return certificates
        
    except Exception as e:
        logging.error(f"Error retrieving certificates: {str(e)}")
        return []


def get_certificate_details(certificate_arn: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """
    Get detailed information for a specific certificate.
    
    Args:
        certificate_arn (str): The ARN of the certificate
        region (str): AWS region
        
    Returns:
        Dict: Certificate details
    """
    try:
        acm_client = boto3.client('acm', region_name=region)
        
        response = acm_client.describe_certificate(CertificateArn=certificate_arn)
        cert_details = response['Certificate']
        
        return {
            'arn': cert_details['CertificateArn'],
            'domain_name': cert_details['DomainName'],
            'subject_alternative_names': cert_details.get('SubjectAlternativeNames', []),
            'status': cert_details['Status'],
            'type': cert_details['Type'],
            'key_algorithm': cert_details.get('KeyAlgorithm', 'N/A'),
            'signature_algorithm': cert_details.get('SignatureAlgorithm', 'N/A'),
            'issued_at': cert_details.get('IssuedAt'),
            'not_before': cert_details.get('NotBefore'),
            'not_after': cert_details.get('NotAfter'),
            'renewal_eligibility': cert_details.get('RenewalEligibility', 'N/A'),
            'in_use': cert_details.get('InUse', False),
            'tags': cert_details.get('Tags', [])
        }
        
    except Exception as e:
        logging.error(f"Error getting details for certificate {certificate_arn}: {str(e)}")
        return {}


def check_certificate_expiration(cert_details: Dict[str, Any], days_threshold: int = 30) -> str:
    """
    Check if certificate is expired or approaching expiration.
    
    Args:
        cert_details (Dict): Certificate details
        days_threshold (int): Days before expiration to flag as 'approaching'
        
    Returns:
        str: 'expired', 'approaching', or 'valid'
    """
    if not cert_details.get('not_after'):
        return 'unknown'
    
    try:
        # Parse the expiration date
        not_after = cert_details['not_after']
        if isinstance(not_after, str):
            exp_date = datetime.fromisoformat(not_after.replace('Z', '+00:00'))
        else:
            exp_date = not_after
            
        # Ensure timezone awareness
        if exp_date.tzinfo is None:
            exp_date = exp_date.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        
        # Calculate days until expiration
        days_until_expiry = (exp_date - now).days
        
        if days_until_expiry < 0:
            return 'expired'
        elif days_until_expiry <= days_threshold:
            return 'approaching'
        else:
            return 'valid'
            
    except Exception as e:
        logging.error(f"Error checking expiration for certificate {cert_details.get('arn', 'unknown')}: {str(e)}")
        return 'error'


def calculate_days_until_expiry(cert_details: Dict[str, Any]) -> int:
    """
    Calculate days until certificate expiration.
    
    Args:
        cert_details (Dict): Certificate details
        
    Returns:
        int: Days until expiration (negative if expired)
    """
    if not cert_details.get('not_after'):
        return None
        
    try:
        not_after = cert_details['not_after']
        if isinstance(not_after, str):
            exp_date = datetime.fromisoformat(not_after.replace('Z', '+00:00'))
        else:
            exp_date = not_after
            
        if exp_date.tzinfo is None:
            exp_date = exp_date.replace(tzinfo=timezone.utc)
            
        now = datetime.now(timezone.utc)
        return (exp_date - now).days
        
    except Exception as e:
        logging.error(f"Error calculating days until expiry: {str(e)}")
        return None


def build_certificate_map(certificates: List[Dict[str, Any]], region: str = 'us-east-1') -> Dict[str, Dict[str, Any]]:
    """
    Build a comprehensive map of certificates with their details and expiration status.
    
    Args:
        certificates (List): List of certificate summaries
        region (str): AWS region
        
    Returns:
        Dict: Map of certificates with ARN as key
    """
    cert_map = {}
    
    for cert_summary in certificates:
        arn = cert_summary['CertificateArn']
        
        # Get detailed certificate information
        cert_details = get_certificate_details(arn, region)
        
        if cert_details:
            # Add expiration status
            cert_details['expiration_status'] = check_certificate_expiration(cert_details)
            cert_details['days_until_expiry'] = calculate_days_until_expiry(cert_details)
            
            cert_map[arn] = cert_details
            
    return cert_map


def format_certificates_for_table(cert_map: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format certificate map into a list of dictionaries suitable for table/Excel export.
    
    Args:
        cert_map (Dict): Certificate map
        
    Returns:
        List[Dict]: Formatted certificate data
    """
    table_data = []
    
    for arn, details in cert_map.items():
        # Extract tags as a readable string
        tags_str = ', '.join([f"{tag['Key']}:{tag['Value']}" for tag in details.get('tags', [])])
        
        # Format SANs as readable string
        sans_str = ', '.join(details.get('subject_alternative_names', []))
        
        row = {
            'Certificate ARN': arn,
            'Domain Name': details.get('domain_name', 'N/A'),
            'Subject Alternative Names': sans_str,
            'Status': details.get('status', 'N/A'),
            'Type': details.get('type', 'N/A'),
            'Key Algorithm': details.get('key_algorithm', 'N/A'),
            'Signature Algorithm': details.get('signature_algorithm', 'N/A'),
            'Issued At': details.get('issued_at', 'N/A'),
            'Not Before': details.get('not_before', 'N/A'),
            'Not After': details.get('not_after', 'N/A'),
            'Days Until Expiry': details.get('days_until_expiry', 'N/A'),
            'Expiration Status': details.get('expiration_status', 'N/A'),
            'Renewal Eligibility': details.get('renewal_eligibility', 'N/A'),
            'In Use': details.get('in_use', False),
            'Tags': tags_str
        }
        
        table_data.append(row)
    
    return table_data


def main():
    """
    Main function to orchestrate the certificate analysis process.
    """
    region = 'us-east-1'  # You can modify this or make it configurable
    
    logging.info("Starting certificate analysis...")
    
    # Step 1: Get all certificates
    certificates = get_all_certificates(region)
    
    if not certificates:
        logging.warning("No certificates found or error occurred")
        return
    
    # Step 2: Build comprehensive certificate map
    cert_map = build_certificate_map(certificates, region)
    
    # Step 3: Format for table/Excel export
    table_data = format_certificates_for_table(cert_map)
    
    # Step 4: Display results
    logging.info(f"\nCertificate Analysis Results:")
    logging.info(f"Total certificates analyzed: {len(table_data)}")
    
    # Count by status
    status_counts = {}
    for cert in table_data:
        status = cert['Expiration Status']
        status_counts[status] = status_counts.get(status, 0) + 1
    
    logging.info(f"Status breakdown: {status_counts}")
    
    # Display certificates that need attention
    expired_certs = [cert for cert in table_data if cert['Expiration Status'] == 'expired']
    approaching_certs = [cert for cert in table_data if cert['Expiration Status'] == 'approaching']
    
    if expired_certs:
        logging.warning(f"\nEXPIRED CERTIFICATES ({len(expired_certs)}):")
        for cert in expired_certs:
            logging.warning(f"  - {cert['Domain Name']} (ARN: {cert['Certificate ARN']})")
    
    if approaching_certs:
        logging.warning(f"\nCERTIFICATES APPROACHING EXPIRATION ({len(approaching_certs)}):")
        for cert in approaching_certs:
            logging.warning(f"  - {cert['Domain Name']} (Expires in {cert['Days Until Expiry']} days)")
    
    # Return the data for potential dashboard/table use
    return {
        'certificate_map': cert_map,
        'table_data': table_data,
        'summary': {
            'total_certificates': len(table_data),
            'status_counts': status_counts,
            'expired_count': len(expired_certs),
            'approaching_count': len(approaching_certs)
        }
    }


if __name__ == "__main__":
    result = main()
    
    # Optionally save to JSON file for dashboard consumption
    if result:
        with open('certificate_analysis.json', 'w') as f:
            json.dump(result, f, indent=2, default=str)
        logging.info("Results saved to certificate_analysis.json")


