from setuptools import setup

setup(
    author='Raymond Sutton',
    author_email='ray.sutton@gmail.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3 :: Only'
    ],
    description='AWS IAM User Account Tool',
    install_requires=['boto3', 'botocore'],
    license='Apache License, Version 2.0',
    name='pythiam',
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
    url='https://github.com/rsutton/pythiam',
    version='1.0.0',
)
