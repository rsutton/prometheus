"""
Helper script for creating IAM User accounts

Examples:
    Create user account, add user to a group and create an AccessKey

        $ python prometheus -u foo -g bar -k

    Add user to multiple groups

        $ python prometheus -u foo -g bar -g baz

    Delete user account

        $ python prometheus -u foo --delete
"""
