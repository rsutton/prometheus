# prometheus

Helper module for managing IAM User accounts

## Examples:

Create user account, add user to a group and create an AccessKey

        $ python -m prometheus create -u foo -g bar -k

Add user to multiple groups

        $ python -m prometheus create -u foo -g bar -g baz

Delete an account

        $ python -m prometheus delete -u foo

Disable an account - removes the account's login profile and deactivates all AccessKeys

        $ python -m prometheus disable -u foo

List all accounts

        $ python -m prometheus list

Create aging report showing accounts without activity in -d days

        $ python -m prometheus report -d 90

