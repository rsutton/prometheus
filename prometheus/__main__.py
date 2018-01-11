import argparse
from datetime import datetime, date
import json
import pickle
import sys

from prometheus.lib.iam_manager import IAMManager
from prometheus.lib.user_record import UserRecordManager
import prometheus._version as version


def parse_args(args):
    p = argparse.ArgumentParser(description="Prometheus: IAM User Creator")
    p.add_argument('--create', dest='create', action='store_true', help='Create User Account')
    p.add_argument('--delete', dest='delete', action='store_true', help='Delete User Account')
    p.add_argument('--disable', dest='disable', action='store_true', help='Disable User Account')
    p.add_argument('--init', dest='init', action='store_true', help='Initialize local data store')
    p.add_argument('--list', dest='list', action='store_true', help='List all users')
    p.add_argument('--report', dest='report', action='store_true', help='List accounts inactive more than 90 days')
    p.add_argument('-u', dest='username', help='IAM User name')
    p.add_argument('-g', dest='group', action='append', help='Use multiple -g for multiple Groups')
    p.add_argument('-k', dest='with_key', action='store_true', help='Create Access Key')
    p.add_argument('-v', '--version', action='store_true', help='Version')
    return p.parse_args(args)


if __name__ == '__main__':
    parser = parse_args(sys.argv[1:])
    name = parser.username
    groups = parser.group

    if parser.version:
        print("Prometheus version: {}".format(version.__version__))
        sys.exit(0)

    iam = IAMManager()

    if parser.create:
        if not name:
            raise argparse.ArgumentError('-u is required')

        # create user
        iam.create_user(name)

        if parser.with_key:
            iam.create_access_key(name)

        if groups is not None:
            user_groups = iam.get_user_groups(name)
            for g in groups:
                if g in user_groups:
                    print("User is already a member of {}.".format(g))
                else:
                    iam.add_user_to_group(name, g)

    elif parser.delete:
        if not name:
            raise argparse.ArgumentError('-u is required')
        iam.delete_user(name)

    elif parser.disable:
        if not name:
            raise argparse.ArgumentError('-u is required')
        iam.disable_user(name)

    elif parser.list:
        for u in iam.list_users():
            print(json.dumps(u, default=str))

    elif parser.report:
        m = UserRecordManager()
        try:
            with open(m.filename, 'rb') as f:
                while True:
                    try:
                        r = pickle.load(f)
                        # skip qtpi resources
                        if "test-App" in str(r.user_name) or "prod-App" in str(r.user_name):
                            continue
                        delta = date.today() - r.last_activity.date()
                        if delta.days > 90:
                            print("{}: {}".format(r.user_name, delta.days))
                    except EOFError:
                        break
        except FileNotFoundError as e:
            print("Data file {} does not exist. Execute --update first".format(m.filename))

    elif parser.init:
        m = UserRecordManager()
        with open(m.filename, 'wb') as f:
            for u in iam.list_users():
                r = m.create_user_record(u.get('UserName'))
                pickle.dump(r, f)
