import boto3
import botocore.client

import json
from prometheus.lib.decorators import boto3_client


class IAMUser(object):
    def __init__(self, user_name):
        self._user_name = user_name
        self._record = {}
        self._access_keys = {}
        self._groups = []
        self._login_profile = None
        self._inline_policies = None
        self._attached_policies = None
        self._mfa_tokens = None
        self._client = None
        self._initialize()

    def _initialize(self):
        self._set_record()
        self._set_user_access_keys()
        self._set_user_groups()
        # self._set_login_profile()
        # self._set_inline_policies()
        # self._set_attached_policies()
        # self._set_mfa_tokens()

    def __repr__(self):
        return json.dumps(self.__dict__, default=str)

    def with_client(self, client):
        assert isinstance(client, botocore.client.BaseClient)
        self._client = client
        return self

    @boto3_client()
    def _set_record(self):
        '''
        {
            Path: /,
            UserName: str,
            UserId: str,
            Arn: str,
            CreateDate: datetime,
            PasswordLastUsed: datetime
        }
        '''
        response = self.client.get_user(UserName=self._user_name)
        self._record = response.get('User')

    @boto3_client()
    def _set_user_access_keys(self):
        response = self.client.list_access_keys(UserName=self._user_name)
        for k in response.get('AccessKeyMetadata'):
            key_id = k.get('AccessKeyId')
            d = self.client.get_access_key_last_used(AccessKeyId=key_id)
            self._access_keys[key_id] = d.get('AccessKeyLastUsed')

    @boto3_client()
    def _set_user_groups(self):
        response = self.client.list_groups_for_user(UserName=self._user_name)
        for g in response.get('Groups'):
            self._groups.append(g.get('GroupName'))

    @property
    def arn(self):
        return self._record.get('Arn')

    @property
    def create_date(self):
        return self._record.get('CreateDate')

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('iam')
        return self._client

    @property
    def password_last_used(self):
        return self._record.get('PasswordLastUsed')

    @property
    def user_groups(self):
        return self._groups

    @property
    def user_id(self):
        return self._record.get('UserId')

    @property
    def user_name(self):
        return self._user_name


