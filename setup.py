from setuptools import setup

about = {}
with open('__about__.py') as fp:
    exec(fp.read(), about)

setup(
    author=about['__author__'],
    author_email=about['__email__'],
    classifiers=about['__classifiers__'],
    description=about['__summary__'],
    install_requires=['boto3', 'botocore'],
    name=about['__title__'],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
    url=about['__uri__'],
    version=about['__version__'],
)
