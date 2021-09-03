from setuptools import setup
from setuptools import find_packages

version = '0.3.0'

with open('README.md') as f:
    readme = f.read()

setup(
    name='certbot-dns-cpanel',
    version=version,
    description='certbot plugin to allow dns based automated certificate issuing in cPanel and to install the certificate.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/badjware/certbot-dns-cpanel',
    author='Massaki Archambault',
    author_email='badjware@massaki.ca',
    license='Apache Licence 2.0',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Security',
        'Topic :: System :: Installation/Setup',
        'Topic :: System :: Networking',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    keywords='certbot letsencrypt cpanel dns-01 installer plugin',
    install_requires=[
        'certbot',
        'zope.interface',
    ],
    entry_points={
        'certbot.plugins': [
            'authenticator = certbot_dns_cpanel.authenticator:Authenticator',
            'installer = certbot_dns_cpanel.installer:Installer',
        ],
    },
)
