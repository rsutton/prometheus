# prometheus

A simple helper for creating and deleting IAM User accounts.

Prometheus uses **boto3** to handle connections with AWS. The existence of an appropriate AWS AccessKey in your shell 
environment is required.

Prometheus uses a simple file cache named **data.db** to reduce AWS API calls and to increase execution speed. The cache
will be created automatically if it does not exist. The cache can be refreshed by use of the 'init' command line parameter.


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

Create/refresh file cache

        $ python -m prometheus init