import argparse
import boto3
import sys

iam = boto3.client('iam')


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


def get_user_groups(user_name):
    err, result = 0, []
    try:
        response = iam.list_groups_for_user(UserName=user_name)
        for g in response.get('Groups'):
            result.append(g.get('GroupName'))
    except Exception as e:
        err = str(e)
    return err, result


def add_user_to_group(user_name, group_name):
    err = None
    try:
        response = iam.add_user_to_group(UserName=user_name, GroupName=group_name)
        http_status_code = response.get('ResponseMetadata').get('HTTPStatusCode')
    except Exception as e:
        err = str(e)
    return err


def create_access_key(user_name):
    err, result = None, {}
    try:
        response = iam.create_access_key(UserName=user_name)
        result = response.get('AccessKey')
    except iam.exceptions.LimitExceededException as e:
        err = str(e)
    return err, result


def get_user_access_keys(user_name):
    err, result = None, []
    try:
        response = iam.list_access_keys(UserName=user_name)
        for k in response.get('AccessKeyMetadata'):
            result.append(k.get('AccessKeyId'))
    except Exception as e:
        err = str(e)
    return err, result


def get_user(user_name):
    err, result = None, {}
    try:
        response = iam.get_user(UserName=user_name)
        result = response.get('User')
    except iam.exceptions.NoSuchEntityException as e:
        err = str(e)
    return err, result


def user_exists(user_name):
    err, result = get_user(user_name)
    return True if len(result) != 0 else False


def create_user(user_name):
    """ Create IAM User account
    Names of users must be alphanumeric, including the following common characters:
    plus (+), equal (=), comma (,), period (.), at (@), underscore (_), and hyphen (-).

    Names of users must be unique within the account. They are not distinguished by case,
     for example, you cannot create users named both "FOO" and "foo".
    """
    err, result = None, {}
    try:
        response = iam.create_user(UserName=user_name)
        result = response.get('User')
    except Exception as e:
        err = str(e)
    return err, result


def delete_user(user_name):
    if not user_exists(user_name):
        print("Delete cancelled! User does not exist: {}".format(user_name))
        sys.exit(1)

    print("Deleting User Account: {}".format(user_name))
    _, user_groups = get_user_groups(user_name)
    for g in user_groups:
        print("Removing user from group: {}".format(g))
        iam.remove_user_from_group(GroupName=g, UserName=user_name)
    _, user_keys = get_user_access_keys(user_name)
    for k in user_keys:
        print("Deleting AccessKey: {}".format(k))
        iam.delete_access_key(UserName=user_name, AccessKeyId=k)
    iam.delete_user(UserName=user_name)
    print("{} deleted.".format(user_name))


def print_dict(dict_obj):
    for k in dict_obj.keys():
        print("\t{}: {}".format(k, dict_obj.get(k)))


def parse_args(args):
    p = argparse.ArgumentParser(description="Prometheus: IAM User Creator")
    p.add_argument('--delete', dest='delete', action='store_true', help='Delete User')
    p.add_argument('-u', dest='username', required=True, help='IAM User name')
    p.add_argument('-g', dest='group', action='append', help='Use multiple -g for multiple Groups')
    p.add_argument('-k', dest='with_key', action='store_true', help='Create Access Key')
    return p.parse_args(args)


if __name__ == '__main__':
    parser = parse_args(sys.argv[1:])
    name = parser.username
    groups = parser.group

    if parser.delete:
        delete_user(name)
        sys.exit(0)

    if user_exists(name):
        print("User already exists.".format(name))
    else:
        error, user = create_user(name)
        if error is None:
            print("Created user {}.".format(user.get('UserName')))
            print_dict(user)
        else:
            print("\nError creating user {}.\n\t{}".format(name, error))
            sys.exit(1)

    if parser.with_key:
        error, key = create_access_key(name)
        if error is None:
            print("Created access key.")
            print_dict(key)
        else:
            print("\nError creating Access Key.\n\t{}".format(error))

    if groups is not None:
        _, user_groups = get_user_groups(name)
        for g in groups:
            if g in user_groups:
                print("User is already a member of {}.".format(g))
            else:
                error = add_user_to_group(name, g)
                if error is not None:
                    print("\nError adding user {} to group {}:\n\t{}".format(name, g, error))
                else:
                    print("Added {} to the {} group.".format(name, g))
