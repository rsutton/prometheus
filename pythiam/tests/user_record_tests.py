import unittest
import boto3
from pythiam.lib.user_record import UserRecordManager, UserRecord
from pythiam.lib.iam_manager import IAMManager


class UserRecordTest(unittest.TestCase):
    client = boto3.client('iam')
    urm = UserRecordManager(filename='../test.db')
    iam = IAMManager()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # def test_record_lifecycle(self):
    #     u = self.iam.get_user('rsutton')
    #     r = self.urm.create_user_record('rsutton', u)
    #     print(r)
    #
    #     u = self.urm.get_user_record('rsutton')
    #     assert isinstance(u, UserRecord)
    #     self.assertEqual('rsutton', u.user_name)
    #     self.assertEqual('arn:aws:iam::594813696195:user/rsutton', u.arn)
    #     self.assertTrue('Cypress' in u.user_groups)
    #     self.assertTrue(len(u.mfa_devices) == 1)
    #
    #     self.urm.delete_user_record('rsutton')
    #     u = self.urm.get_user_record('rsutton')
    #     self.assertIsNone(u)

    def test_groups(self):
        self.urm.load_data()
        for r in self.urm.records.keys():
            u = self.urm.records[r]
            assert isinstance(u, UserRecord)
            print(u.last_activity)
