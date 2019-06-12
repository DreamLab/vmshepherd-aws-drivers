import io
import re
from os.path import abspath, dirname, join

from setuptools import find_packages, setup


def read(name):
    here = abspath(dirname(__file__))
    return io.open(
        join(here, name), encoding='utf8'
    ).read()


setup(
    name="vmshepherd-aws-drivers",
    version="1.0.0",
    author='Dreamlab - PaaS KRK',
    author_email='paas-support@dreamlab.pl',
    url='https://github.com/Dreamlab/vmshepherd-aws-drivers',
    description='AWS drivers for VmShepherd',
    long_description='%s\n%s' % (
        read('README.rst'),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=read('requirements.txt').split('\n'),
    zip_safe=False,
    entry_points={
        'vmshepherd.driver.iaas': [
            'AwsIaaSDriver = vmshepherd_aws_drivers:AwsIaaSDriver'
        ],
        'vmshepherd.driver.presets': [
            'AwsPresetDriver = vmshepherd_aws_drivers:AwsPresetDriver'
        ]
    },
    keywords=['vmshepherd', 'AWS', 'ASG'],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX'
    ]
)
