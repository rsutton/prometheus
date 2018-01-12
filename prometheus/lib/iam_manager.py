import boto3
from prometheus.lib.decorators import boto3_client


class IAMManager(object):
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('iam')
        return self._client

    def user_exists(self, user_name):
        result = self.get_user(user_name) or {}
        return True if 'UserName' in result else False

    @boto3_client()
    def add_user_to_group(self, user_name, group_name):
        self.client.add_user_to_group(UserName=user_name, GroupName=group_name)
        print("Added user {} to group {}.".format(user_name, group_name))

    @boto3_client()
    def create_access_key(self, user_name):
        response = self.client.create_access_key(UserName=user_name)
        print("Created AccessKey for user {}".format(user_name))
        print(response.get('AccessKey'))

    @boto3_client()
    def create_user(self, user_name):
        """ Create IAM User account
        Names of users must be alphanumeric, including the following common characters:
        plus (+), equal (=), comma (,), period (.), at (@), underscore (_), and hyphen (-).

        Names of users must be unique within the account. They are not distinguished by case,
         for example, you cannot create users named both "FOO" and "foo".
        """
        result = None
        if self.user_exists(user_name):
            print("User already exists.".format(user_name))
        else:
            response = self.client.create_user(UserName=user_name)
            result = response.get('User')
            print("Created user: {}".format(user_name))
        return result

    @boto3_client()
    def deactivate_user_keys(self, user_name, keys):
        for key_id in keys.keys():
            self.client.update_access_key(UserName=user_name, AccessKeyId=key_id, Status='Inactive')

    @boto3_client()
    def delete_login_profile(self, user_name):
        self.client.delete_login_profile(UserName=user_name)

    @boto3_client()
    def delete_user_keys(self, user_name, keys):
        for key_id in keys.keys():
            print("Deleting AccessKey: {}".format(key_id))
            self.client.delete_access_key(UserName=user_name, AccessKeyId=key_id)

    @boto3_client()
    def delete_inline_policies(self, user_name, policies):
        for p in policies:
            print("Deleting Inline Policy {}".format(p))
            self.client.delete_user_policy(UserName=user_name, PolicyName=p)

    @boto3_client()
    def delete_mfa_devices(self, user_name, devices):
        for d in devices:
            self.client.deactivate_mfa_device(UserName=user_name, SerialNumber=d)
            self.client.delete_virtual_mfa_device(SerialNumber=d)

    @boto3_client()
    def delete_user(self, user_name):
        self.client.delete_user(UserName=user_name)

    @boto3_client()
    def detach_managed_policies(self, user_name, policies):
        for p in policies:
            print("Detaching Managed Policy {}".format(p))
            self.client.detach_user_policy(UserName=user_name, PolicyArn=p)

    @boto3_client()
    def get_access_key_last_used(self, key_id):
        response = self.client.get_access_key_last_used(AccessKeyId=key_id)
        return response.get('AccessKeyLastUsed')

    @boto3_client()
    def get_login_profile(self, user_name):
        response = self.client.get_login_profile(UserName=user_name)
        return response.get('LoginProfile')

    @boto3_client()
    def get_user(self, user_name):
        response = self.client.get_user(UserName=user_name)
        return response.get('User')

    @boto3_client()
    def get_user_groups(self, user_name):
        result = []
        response = self.client.list_groups_for_user(UserName=user_name)
        for g in response.get('Groups'):
            result.append(g.get('GroupName'))
        return result

    @boto3_client()
    def list_access_keys(self, user_name):
        paginator = self.client.get_paginator('list_access_keys')
        for p in paginator.paginate(UserName=user_name):
            for y in p.get('AccessKeyMetadata'):
                yield y

    @boto3_client()
    def list_attached_policies(self, user_name):
        paginator = self.client.get_paginator('list_attached_user_policies')
        for p in paginator.paginate(UserName=user_name):
            for y in p.get('AttachedPolicies'):
                yield y

    @boto3_client()
    def list_groups_for_user(self, user_name):
        paginator = self.client.get_paginator('list_groups_for_user')
        for p in paginator.paginate(UserName=user_name):
            for y in p.get('Groups'):
                yield y

    @boto3_client()
    def list_mfa_devices(self, user_name):
        paginator = self.client.get_paginator('list_mfa_devices')
        for p in paginator.paginate(UserName=user_name):
            for y in p.get('MFADevices'):
                yield y

    @boto3_client()
    def list_user_policies(self, user_name):
        paginator = self.client.get_paginator('list_user_policies')
        for p in paginator.paginate(UserName=user_name):
            for y in p.get('PolicyNames'):
                yield y

    @boto3_client()
    def list_users(self):
        paginator = self.client.get_paginator('list_users')
        for p in paginator.paginate():
            for y in p.get('Users'):
                yield y

    @boto3_client()
    def remove_user_from_groups(self, user_name, groups):
        for g in groups:
            self.client.remove_user_from_group(GroupName=g, UserName=user_name)
