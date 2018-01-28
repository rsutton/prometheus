import botocore.exceptions


def boto3_client():
    def _outer(func):
        def _inner(*args, **kwargs):
            response = None
            try:
                response = func(*args, **kwargs)
            except botocore.exceptions.ClientError as e:
                if 'NoSuchEntity' in str(e):
                    pass
                else:
                    print(str(e))
            return response

        return _inner

    return _outer
