import argparse
from datetime import date
import os.path
from shutil import copyfile

import sys

from pythiam.lib.iam_manager import IAMManager
from pythiam.lib.user_record import UserRecordManager, UserRecord


def parse_args(args):
    p = argparse.ArgumentParser(prog='pythiam', description='AWS IAM Helper', add_help=True)
    subparsers = p.add_subparsers()

    parser_create = subparsers.add_parser('create', help='Create IAM User Account')
    parser_create.set_defaults(func=create)
    parser_create.add_argument('-u', dest='username', required=True, help='IAM User name')
    parser_create.add_argument('-g', dest='groups', action='append', help='Use multiple -g for multiple Groups')
    parser_create.add_argument('-k', dest='with_key', action='store_true', help='Create Access Key')

    parser_delete = subparsers.add_parser('delete', help='Delete IAM User Account')
    parser_delete.set_defaults(func=delete)
    parser_delete.add_argument('-u', dest='username', required=True, help='IAM User name')

    parser_disable = subparsers.add_parser('disable', help='Disable IAM User Account')
    parser_disable.set_defaults(func=disable)
    parser_disable.add_argument('-u', dest='username', required=True, help='IAM User name')

    parser_init = subparsers.add_parser('init', help='Initialize data file')
    parser_init.set_defaults(func=init)

    parser_list = subparsers.add_parser('list', help='List all IAM accounts')
    parser_list.set_defaults(func=list_users)

    parser_report = subparsers.add_parser('report', help='Aging Report')
    parser_report.add_argument('-d', dest='days', required=True, help='Inactive more than -d days')
    parser_report.set_defaults(func=report)

    return p.parse_args(args)


def create(args):
    iam = IAMManager()
    urm = UserRecordManager().with_iam(iam)
    urm.load_data()

    # create user in IAM
    user_data = iam.create_user(args.username)

    if args.with_key:
        iam.create_access_key(args.username)

    if args.groups is not None:
        user_groups = iam.get_user_groups(args.username)
        for g in args.groups:
            if g in user_groups:
                print("User is already a member of {}".format(g))
            else:
                iam.add_user_to_group(args.username, g)
    urm.create_user_record(args.username, user_data)


def delete(args):
    iam = IAMManager()
    urm = UserRecordManager().with_iam(iam)
    urm.load_data()

    record = urm.get_user_record(args.username)
    if record is None:
        return
    assert isinstance(record, UserRecord)

    print("Deleting User Account: {}".format(args.username))
    iam.delete_user_keys(args.username, record.access_keys)
    iam.remove_user_from_groups(args.username, record.groups)
    iam.delete_login_profile(args.username)
    iam.delete_inline_policies(args.username, record.inline_policies)
    iam.detach_managed_policies(args.username, record.attached_policies)
    iam.delete_mfa_devices(args.username, record.mfa_devices)
    iam.delete_user(args.username)
    urm.delete_user_record(args.username)
    print("... {} deleted".format(args.username))


def disable(args):
    iam = IAMManager()
    urm = UserRecordManager().with_iam(iam)
    urm.load_data()

    record = urm.get_user_record(args.username)
    if record is None:
        return
    assert isinstance(record, UserRecord)

    print("Disabling User Account: {}".format(args.username))
    iam.deactivate_user_keys(args.username, record.access_keys)
    iam.delete_login_profile(args.username)
    print("... {} disabled".format(args.username))


def init(args):
    urm = UserRecordManager()
    urm.load_data()
    if os.path.exists(urm.filename):
        copyfile(urm.filename, "{}.bak".format(urm.filename))
        os.remove(urm.filename)
    urm.load_data()


def list_users(args):
    urm = UserRecordManager()
    urm.load_data()
    for k in urm.records.keys():
        print(urm.records[k])


def report(args):
    urm = UserRecordManager()
    urm.load_data()
    for k in urm.records.keys():
        r = urm.records[k]
        delta = date.today() - r.last_activity.date()
        if delta.days > int(args.days):
            print("{}: {}".format(r.user_name, delta.days))


if __name__ == '__main__':
    args = ['-h'] if len(sys.argv[1:]) == 0 else sys.argv[1:]
    parser = parse_args(args)
    if hasattr(parser, 'func'):
        parser.func(parser)
    else:
        print("Error parsing arguments.")
