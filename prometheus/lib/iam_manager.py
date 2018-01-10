import boto3
import json
from prometheus.lib.decorators import boto3_client


class IAMManager(object):
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('iam')
        return self._client

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
        else:
            response = self.client.create_user(UserName=user_name)
            print("Created user: {}".format(response.get('User')))

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
    def get_user_groups(self, user_name):
        result = []
        response = self.client.list_groups_for_user(UserName=user_name)
        for g in response.get('Groups'):
            result.append(g.get('GroupName'))
        return result

    @boto3_client()
    def remove_user_from_groups(self, user_name):
        for g in self.get_user_groups(user_name):
            self.client.remove_user_from_group(GroupName=g, UserName=user_name)

    @boto3_client()
    def delete_user_keys(self, user_name):
        response = self.client.list_access_keys(UserName=user_name)
        for key in response.get('AccessKeyMetadata'):
            key_id = key.get('AccessKeyId')
            print("Deleting AccessKey: {}".format(key_id))
            self.client.delete_access_key(UserName=user_name, AccessKeyId=key_id)

    @boto3_client()
    def delete_login_profile(self, user_name):
        response = self.client.get_login_profile(UserName=user_name)
        if 'LoginProfile' in response:
            print("Deleting Login Profile")
            self.client.delete_login_profile(UserName=user_name)

    @boto3_client()
    def detach_managed_policies(self, user_name):
        response = self.client.list_attached_user_policies(UserName=user_name)
        for p in response.get('AttachedPolicies'):
            policy = p.get('PolicyArn')
            print("Detaching Managed Policy {}".format(policy))
            self.client.detach_user_policy(UserName=user_name, PolicyArn=policy)

    @boto3_client()
    def delete_inline_policies(self, user_name):
        response = self.client.list_user_policies(UserName=user_name)
        for p in response.get('PolicyNames'):
            print("Deleting Inline Policy {}".format(p))
            self.client.delete_user_policy(UserName=user_name, PolicyName=p)

    def delete_user(self, user_name):
        if not self.user_exists(user_name):
            print("Delete cancelled! User does not exist: {}".format(user_name))
            return
        print("Deleting User Account: {}".format(user_name))

        self.delete_user_keys(user_name)
        self.remove_user_from_groups(user_name)
        self.delete_login_profile(user_name)
        self.delete_inline_policies(user_name)
        self.detach_managed_policies(user_name)

        self.client.delete_user(UserName=user_name)
        print("... {} deleted.".format(user_name))

    @boto3_client()
    def list_users(self):
        paginator = self.client.get_paginator('list_users')
        page_iter = paginator.paginate()

        for p in page_iter:
            for u in p.get('Users'):
                print(json.dumps(u, default=str))
