"""
Helper script for creating IAM User accounts

Examples:
    Create user account with user name `foo`, add to group `bar`, and create an AccessKey

        $ python prometheus.py -u foo -g bar -k

    Add user to multiple groups

        $ python prometheus.py -u foo -g bar -g baz

"""
