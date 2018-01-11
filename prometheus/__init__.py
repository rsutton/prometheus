"""
Helper module for creating IAM User accounts

Examples:

Create user account, add user to a group and create an AccessKey

        $ python -m prometheus --create -u foo -g bar -k

Add user to multiple groups

        $ python -m prometheus --create -u foo -g bar -g baz

Delete an account

        $ python -m prometheus --delete -u foo

Disable an account - removes the account's login profile and deactivates all AccessKeys

        $ python -m prometheus --disable -u foo
"""
