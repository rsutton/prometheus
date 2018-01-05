import argparse
import boto3
import sys
import json

iam = boto3.client('iam')

def get_user(user_name):
    err, user = None, {}
    try:
        response = iam.get_user(UserName=user_name)
        user = response.get('User')
    except iam.exceptions.NoSuchEntityException as e:
        err = str(e)
    return err, user

def user_exists(user_name):
    err, user = get_user(user_name)
    return True if len(user) != 0 else False

def make_user(user_name):
    response = iam.create_user(UserName=user_name)
    return response.get('User')

def get_group(group_name):
    err, group, users = None, {}, {}
    try:
        response = iam.get_group(GroupName=group_name)
        group = response.get('Group')
        users = response.get('Users')
    except iam.exceptions.NoSuchEntityException as e:
        err = str(e)
    return err, group, users

def group_exists(group_name):
    _, group, _ = get_group(group_name)
    return True if len(group) != 0 else False

def add_user_to_group(user_name, group_name):
    err = None
    # if not group_exists(group_name):
    #     err = "Group {} does not exist.".format(group_name)
    try:
        response = iam.add_user_to_group(UserName=user_name, GroupName=group_name)
        http_status_code = response.get('ResponseMetadata').get('HTTPStatusCode')
    except Exception as e:
        err = str(e)
    return err

def create_access_key(user_name):
    err, key = None, {}
    try:
        response = iam.create_access_key(UserName=user_name)
        key = response.get('AccessKey')
    except iam.exceptions.LimitExceededException as e:
        err = str(e)
    return err, key

def parse_args(args):
    parser = argparse.ArgumentParser(description="Prometheus: IAM User Creator")
    parser.add_argument('-u', dest='username', required=True, help='IAM User name' )
    parser.add_argument('-g', dest='group', action='append', help='Use multiple -g for multiple Groups')
    parser.add_argument('-k', dest='with_key', action='store_true', help='Create Access Key')
    return parser.parse_args(args)


if __name__ == '__main__':
    parser = parse_args(sys.argv[1:])
    name = parser.username
    groups = parser.group

    if user_exists(name):
        print("User already exists!".format(name))
        _, user = get_user(name)
        for k in user.keys():
            print("\t{}: {}".format(k, user.get(k)))
    else:
        user = make_user(name)
        print("Created user {}.".format(user.get('UserName')))

    if parser.with_key:
        err, key = create_access_key(name)
        if err is None:
            print("Created access key.")
            for k in key.keys():
                print("\t{}: {}".format(k, key.get(k)))
        else:
            print("\nError creating Access Key.\n\t{}".format(err))

    if groups is not None:
        for group in groups:
            err = add_user_to_group(name, group)
            if err is not None:
                print("\nError adding user {} to group {}:\n\t{}".format(name, group, err))
            else:
                print("Added {} to the {} group.".format(name, group))
