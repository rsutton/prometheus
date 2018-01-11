import boto3
from prometheus.lib.decorators import boto3_client
from prometheus.lib.user_record import UserRecordManager


class IAMManager(object):
    def __init__(self):
        self._client = None
        self._record_manager = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('iam')
        return self._client

    @property
    def record_manager(self):
        if self._record_manager is None:
            self._record_manager = UserRecordManager()
        return self._record_manager

    @boto3_client()
    def get_user(self, user_name):
        response = self.client.get_user(UserName=user_name)
        return response.get('User')

    def user_exists(self, user_name):
        result = self.get_user(user_name) or {}
        return True if 'UserName' in result else False

    @boto3_client()
    def create_user(self, user_name):
        """ Create IAM User account
        Names of users must be alphanumeric, including the following common characters:
        plus (+), equal (=), comma (,), period (.), at (@), underscore (_), and hyphen (-).

        Names of users must be unique within the account. They are not distinguished by case,
         for example, you cannot create users named both "FOO" and "foo".
        """
        if self.user_exists(user_name):
            print("User already exists.".format(user_name))
            return False
        else:
            response = self.client.create_user(UserName=user_name)
            print("Created user: {}".format(response.get('User')))
            return True

    @boto3_client()
    def get_user_groups(self, record):
        result = []
        response = self.client.list_groups_for_user(UserName=record.user_name)
        for g in response.get('Groups'):
            result.append(g.get('GroupName'))

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
    def remove_user_from_groups(self, record):
        for g in record.user_groups:
            self.client.remove_user_from_group(GroupName=g, UserName=record.user_name)

    @boto3_client()
    def deactivate_user_keys(self, record):
        for key_id in record.access_keys.keys():
            self.client.update_access_key(UserName=record.user_name, AccessKeyId=key_id, Status='Inactive')

    @boto3_client()
    def delete_user_keys(self, record):
        for key_id in record.access_keys.keys():
            print("Deleting AccessKey: {}".format(key_id))
            self.client.delete_access_key(UserName=record.user_name, AccessKeyId=key_id)

    @boto3_client()
    def delete_login_profile(self, record):
        if record.login_profile:
            self.client.delete_login_profile(UserName=record.user_name)

    @boto3_client()
    def detach_managed_policies(self, record):
        for p in record.attached_policies:
            print("Detaching Managed Policy {}".format(p))
            self.client.detach_user_policy(UserName=record.user_name, PolicyArn=p)

    @boto3_client()
    def delete_inline_policies(self, record):
        for p in record.inline_policies:
            print("Deleting Inline Policy {}".format(p))
            self.client.delete_user_policy(UserName=record.user_name, PolicyName=p)

    @boto3_client()
    def delete_mfa_devices(self, record):
        for d in record.mfa_devices:
            self.client.deactivate_mfa_device(UserName=record.user_name, SerialNumber=d)
            self.client.delete_virtual_mfa_device(SerialNumber=d)

    def delete_user(self, user_name):
        r = self.record_manager.create_user_record(user_name)

        if not r.user_id:
            print("Delete cancelled! User does not exist: {}".format(user_name))
            return False

        print("Deleting User Account: {}".format(user_name))
        self.delete_user_keys(r)
        self.remove_user_from_groups(r)
        self.delete_login_profile(r)
        self.delete_inline_policies(r)
        self.detach_managed_policies(r)
        self.delete_mfa_devices(r)

        self.client.delete_user(UserName=user_name)
        print("... {} deleted.".format(user_name))
        return True

    def disable_user(self, user_name):
        r = self.record_manager.create_user_record(user_name)

        if not r.user_id:
            print("Delete cancelled! User does not exist: {}".format(user_name))
            return False

        print("Disabling User Account: {}".format(user_name))
        self.deactivate_user_keys(r)
        self.delete_login_profile(r)
        print("... {} disabled.".format(user_name))

    @boto3_client()
    def list_users(self):
        paginator = self.client.get_paginator('list_users')
        page_iter = paginator.paginate()

        for p in page_iter:
            for u in p.get('Users'):
                yield u

