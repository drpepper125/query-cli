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


