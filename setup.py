from setuptools import setup
from setuptools import find_packages


setup(
    name='certbot-dns-cpanel',
    package=find_packages(),
    install_requires=[
        'certbot',
        'zope.interface',
    ],
    entry_points={
        'certbot.plugins': [
            'authenticator = certbot_dns_cpanel.dns_cpanel:Authenticator',
        ],
    },
)
