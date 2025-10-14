import aws_helper
import get_certs
import get_ec2
from set_context import select_account_interactive
import get_lb


# get account context 
env, account_id, account_name = select_account_interactive('account_lists.json')

mgmt_session = aws_helper.create_mgmt_session(env,account_id)
read_only_ession = aws_helper.create_read_only_session(mgmt_session,"ReadOnlyAccess")

certs = get_certs.get_all_certificates(read_only_ession)
ec2 = get_ec2.get_ec2_instances(read_only_ession)
lb = get_lb.get_load_balancers(read_only_ession)

print(certs)
print(ec2)
print(lb)

aws_helper.end_session(mgmt_session)
aws_helper.end_session(read_only_ession)