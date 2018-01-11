import boto3
import botocore.client

import json
from prometheus.lib.decorators import boto3_client


class UserRecordManager(object):
    def __init__(self):
        self._client = None

    def with_client(self, client):
        assert isinstance(client, botocore.client.BaseClient)
        self._client = client
        return self

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('iam')
        return self._client

    def create_user_record(self, user_name):
        record = UserRecord(user_name)
        self._set_iam_data(record)
        if record.user_id is not None:
            self._set_user_access_keys(record)
            self._set_user_groups(record)
            self._set_login_profile(record)
            self._set_inline_policies(record)
            self._set_attached_policies(record)
            self._set_mfa_devices(record)
        return record

    @boto3_client()
    def _set_iam_data(self, record):
        """
        {
            Path: /,
            UserName: str,
            UserId: str,
            Arn: str,
            CreateDate: datetime,
            PasswordLastUsed: datetime
        }
        """
        response = self.client.get_user(UserName=record.user_name)
        record._iam_data = response.get('User')

    @boto3_client()
    def _set_login_profile(self, record):
        response = self.client.get_login_profile(UserName=record.user_name)
        record._login_profile = response.get('LoginProfile')

    @boto3_client()
    def _set_attached_policies(self, record):
        response = self.client.list_attached_user_policies(UserName=record.user_name)
        for p in response.get('AttachedPolicies'):
            record._attached_policies.append(p.get('PolicyArn'))

    @boto3_client()
    def _set_inline_policies(self, record):
        response = self.client.list_user_policies(UserName=record.user_name)
        for p in response.get('PolicyNames'):
            record._inline_policies.append(p)

    @boto3_client()
    def _set_user_access_keys(self, record):
        response = self.client.list_access_keys(UserName=record.user_name)
        for k in response.get('AccessKeyMetadata'):
            key_id = k.get('AccessKeyId')
            d = self.client.get_access_key_last_used(AccessKeyId=key_id)
            record._access_keys[key_id] = d.get('AccessKeyLastUsed')

    @boto3_client()
    def _set_user_groups(self, record):
        response = self.client.list_groups_for_user(UserName=record.user_name)
        for g in response.get('Groups'):
            record._groups.append(g.get('GroupName'))

    @boto3_client()
    def _set_mfa_devices(self, record):
        response = self.client.list_mfa_devices(UserName=record.user_name)
        for m in response.get('MFADevices'):
            record._mfa_devices.append(m.get('SerialNumber'))

class UserRecord(object):
    def __init__(self, user_name):
        self._access_keys = {}
        self._attached_policies = []
        self._groups = []
        self._iam_data = {}
        self._inline_policies = []
        self._login_profile = {}
        self._mfa_devices = []
        self._user_name = user_name

    def __repr__(self):
        return json.dumps(self.__dict__, default=str)

    @property
    def access_keys(self):
        return self._access_keys

    @property
    def arn(self):
        return self._iam_data.get('Arn')

    @property
    def attached_policies(self):
        return self._attached_policies

    @property
    def creation_date(self):
        return self._iam_data.get('CreateDate')

    @property
    def inline_policies(self):
        return self._inline_policies

    @property
    def login_profile(self):
        return self._login_profile

    @property
    def mfa_devices(self):
        return self._mfa_devices

    @property
    def password_last_used(self):
        return self._iam_data.get('PasswordLastUsed')

    @property
    def user_groups(self):
        return self._groups

    @property
    def user_id(self):
        return self._iam_data.get('UserId')

    @property
    def user_name(self):
        return self._user_name

    @property
    def last_activity(self):
        events = list()
        events.append(self._iam_data.get('CreateDate'))
        d = self.password_last_used
        if d:
            events.append(self.password_last_used)
        for k in self.access_keys:
            d = self.access_keys.get(k).get('LastUsedDate')
            if d:
                events.append(d)
        events = sorted(events, reverse=True)
        return events[0]

