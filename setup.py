from setuptools import setup

about = {}
with open('prometheus/__about__.py') as fp:
    exec(fp.read(), about)

setup(
    author=about['author'],
    author_email=about['email'],
    description=about['summary'],
    install_requires=['boto3', 'botocore'],
    name=about['title'],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
    url=about['uri'],
    version=about['version'],
)
