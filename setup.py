from setuptools import setup, find_packages

exec(open('prometheus/_version.py').read())

setup(
    name="prometheus",
    version=__version__,
    description="AWS IAM Management Tool",
    long_description=open("README.md").read(),
    author="Ray Sutton",
    author_email="ray.sutton@gmail.com",

    data_files=[],

    packages=find_packages(exclude=['tests*']),
    package_data={'': ['templates/*']},

    install_requires=['boto3'],
    test_suite='nose.collector',
    tests_require=['nose', 'mock'],

    include_package_data=True
)
