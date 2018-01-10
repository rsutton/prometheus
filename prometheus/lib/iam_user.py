import boto3
import json
from prometheus.lib.decorators import boto3_client


class IAMUser(object):
    def __init__(self, user_name):
        self._user_name = user_name
        self._password_last_used = None #u.get('PasswordLastUsed')
        self._access_keys = []
        self._keys_last_used = {}
        self._groups = []
        self._client = None
        self._initialize()

    def _initialize(self):
        self._set_user_access_keys()
        for k in self._access_keys:
            _, d = self._get_access_key_last_used(k)
            self._keys_last_used[k] = str(d)
        self._set_user_groups()

    def __repr__(self):
        return json.dumps(self.__dict__)

    @boto3_client()
    def _set_user_access_keys(self):
        response = self.client.list_access_keys(UserName=self._user_name)
        for k in response.get('AccessKeyMetadata'):
            self._access_keys.append(k.get('AccessKeyId'))

    @boto3_client()
    def _get_access_key_last_used(self, key_id):
        response = self.client.get_access_key_last_used(AccessKeyId=key_id)
        return response.get('AccessKeyLastUsed')

    @boto3_client()
    def _set_user_groups(self):
        response = self.client.list_groups_for_user(UserName=self._user_name)
        for g in response.get('Groups'):
            self._groups.append(g.get('GroupName'))

    def with_client(self, client):
        assert client.isinstance(boto3.client)
        self._client = client
        return self

    @property
    def client(self):
        if self._client is None:
            self._client = boto3.client('iam')
        return self._client

    @property
    def user_groups(self):
        return self._groups
