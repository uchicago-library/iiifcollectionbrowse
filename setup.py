from setuptools import setup, find_packages


def readme():
    with open("README.md", 'r') as f:
        return f.read()


setup(
    name="iiifcollectionbrowse",
    description="Browses IIIF collections",
    version="0.0.1",
    long_description=readme(),
    author="Brian Balsamo",
    author_email="brian@brianbalsamo.com",
    packages=find_packages(
        exclude=[
        ]
    ),
    include_package_data=True,
    url='https://github.com/uchicago-library/iiifcollectionbrowse',
    install_requires=[
        'Flask'
    ],
    tests_require=[
        'pytest'
    ],
    test_suite='tests'
)
