import boto3
import logging
from set_context import select_account_interactive
# root session
root_sts_client = boto3.client('sts')
env, account_id, account_name = 'pro', '123456789012', 'test-pro-admin'


# mgmt session function
def create_mgmt_session(client, env,):
    match env:
        case 'pro':
            pro_mgmt_session = client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{account_name}',
                RoleSessionName='mgmt-session'
            )
            return boto3.Session(
                aws_access_key_id=pro_mgmt_session['Credentials']['AccessKeyId'],
                aws_secret_access_key=pro_mgmt_session['Credentials']['SecretAccessKey'],
                aws_session_token=pro_mgmt_session['Credentials']['SessionToken']
            )
        case 'dev':
            dev_mgmt_session = client.assume_role(
                RoleArn=f'arn:aws:iam::{account_id}:role/{account_name}',
                RoleSessionName='mgmt-session'
            )
            return boto3.Session(
                aws_access_key_id=dev_mgmt_session['Credentials']['AccessKeyId'],
                aws_secret_access_key=dev_mgmt_session['Credentials']['SecretAccessKey'],
                aws_session_token=dev_mgmt_session['Credentials']['SessionToken']
            )
        case _:
            raise ValueError(f"Invalid environment: {env}")


def create_read_only_session(mgmt_session,account_id,role_name):
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    sts_client = mgmt_session.client('sts')
    read_only_creds = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='read-only-session'
    )
    return boto3.Session(
        aws_access_key_id=read_only_creds['Credentials']['AccessKeyId'],
        aws_secret_access_key=read_only_creds['Credentials']['SecretAccessKey'],
        aws_session_token=read_only_creds['Credentials']['SessionToken']
    )


def end_session(session):
    session.close()
    logging.info(f"Session closed for")