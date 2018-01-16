import json
import os.path
import pickle

from prometheus.lib.iam_manager import IAMManager
from prometheus.lib.utils import file_age


class UserRecordManager(object):
    def __init__(self, *args, **kwargs):
        self._client = None
        self._filename = kwargs.get('filename') or 'data.db'
        self._iam = None
        self._records = {}

    def with_file(self, filename):
        self._filename = filename
        self.load_data()
        return self

    def with_iam(self, iam):
        self._iam = iam
        return self

    @property
    def filename(self):
        return self._filename

    @property
    def iam(self):
        if self._iam is None:
            self._iam = IAMManager()
        return self._iam

    @property
    def records(self):
        return self._records

    @records.setter
    def records(self, value):
        self._records = value

    def create_user_record(self, user_name, data):
        record = UserRecord(user_name)
        self._set_iam_data(record, data)
        self._set_user_access_keys(record)
        self._set_user_groups(record)
        self._set_login_profile(record)
        self._set_inline_policies(record)
        self._set_attached_policies(record)
        self._set_mfa_devices(record)
        self.records[user_name] = record
        self.write_record_to_disk(record)
        return record

    def delete_user_record(self, user_name):
        new_records = dict(self.records)
        del new_records[user_name]
        self.records = new_records
        self.write_all_records_to_disk()

    def get_user_record(self, user_name):
        record = self._records.get(user_name)
        if record is None:
            print("User account {} not found in data file".format(user_name))
            print("Looking up account in IAM")
            user_data = self.iam.get_user(user_name)
            if not user_data:
                print("... not found in IAM")
            else:
                record = self.create_user_record(user_name, user_data)
        return record

    def load_data(self):
        if not os.path.exists(self.filename):
            print("User record data file not found. Creating new file: {}".format(self.filename))
            with open(self.filename, 'wb') as f:
                for u in self.iam.list_users():
                    n = u.get('UserName')
                    print("Processing record: {}".format(n))
                    r = self.create_user_record(n, u)
                    self.write_record_to_disk(r)

        if file_age(self.filename) > 2:
            print("Data file is more than 2 days old, consider refreshing.")

        with open(self.filename, 'rb') as f:
            while True:
                try:
                    r = pickle.load(f)
                    assert isinstance(r, UserRecord)
                    self.records[r.user_name] = r
                except EOFError:
                    break

    def write_all_records_to_disk(self):
        # replace data file with contents of new_records
        with open(self.filename, 'wb') as f:
            f.truncate()
        with open(self.filename, 'ab') as f:
            for k in self.records.keys():
                pickle.dump(self.records[k], f)

    def write_record_to_disk(self, record):
        with open(self.filename, 'ab') as f:
            pickle.dump(record, f)

    @staticmethod
    def _set_iam_data(record, data):
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
        record.iam_data = data

    def _set_login_profile(self, record):
        record.login_profile = self.iam.get_login_profile(record.user_name)

    def _set_attached_policies(self, record):
        for p in self.iam.list_attached_policies(record.user_name):
            record.attached_policies.append(p.get('PolicyArn'))

    def _set_inline_policies(self, record):
        for p in self.iam.list_user_policies(record.user_name):
            record.inline_policies.append(p)

    def _set_user_access_keys(self, record):
        for k in self.iam.list_access_keys(record.user_name):
            key_id = k.get('AccessKeyId')
            record.access_keys[key_id] = self.iam.get_access_key_last_used(key_id)

    def _set_user_groups(self, record):
        for g in self.iam.list_groups_for_user(record.user_name):
            record.groups.append(g.get('GroupName'))

    def _set_mfa_devices(self, record):
        for m in self.iam.list_mfa_devices(record.user_name):
            record.mfa_devices.append(m.get('SerialNumber'))


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
    def groups(self):
        return self._groups

    @property
    def iam_data(self):
        return self._iam_data

    @iam_data.setter
    def iam_data(self, value):
        self._iam_data = value

    @property
    def inline_policies(self):
        return self._inline_policies

    @property
    def login_profile(self):
        return self._login_profile

    @login_profile.setter
    def login_profile(self, value):
        self._login_profile = value

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
        # add account creation date
        events.append(self.iam_data.get('CreateDate'))

        # last password usage
        d = self.password_last_used
        if d:
            events.append(self.password_last_used)

        # last access key usage
        for k in self.access_keys:
            d = self.access_keys.get(k).get('LastUsedDate')
            if d:
                events.append(d)

        # return most recent
        events = sorted(events, reverse=True)
        return events[0]
