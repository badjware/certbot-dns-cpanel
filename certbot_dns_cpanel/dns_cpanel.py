"""cPanel dns-01 authenticator plugin"""
import zope.interface

from certbot import interfaces
from certbot.plugins import dns_common


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """cPanel dns-01 authenticator plugin"""

    description = "Obtain a certificate using a DNS TXT record in cPanel"
    problem = "a"

    def __init__(self, *args, **kwargs):
        super(Authenticator, self).__init__(*args, **kwargs)
        self.credentials = None

    @classmethod
    def add_parser_arguments(cls, add):
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=10)
        add("credentials",
            type=str,
            help="The cPanel credentials INI file")

    def more_info(self):
        return self.description

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'The cPanel credentials INI file',
            {
                'host': 'cPanel host',
                'port': 'cPanel port',
                'accountid': 'cPanel account id',
                'username': 'cPanel username',
                'password': 'cPanel password'
            }
        )

    def _perform(self, domain, validation_domain_name, validation):
        pass

    def _cleanup(self, domain, validation_domain_name, validation):
        pass

class _CPanelClient:
    pass
