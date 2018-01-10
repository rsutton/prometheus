# prometheus

Helper module for managing IAM User accounts

## Examples:

Create user account, add user to a group and create an AccessKey

        $ python -m prometheus -u foo -g bar -k

Add user to multiple groups

        $ python -m prometheus -u foo -g bar -g baz

Delete user account

        $ python -m prometheus -u foo --delete
