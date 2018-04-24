"""Example Certbot plugins.

For full examples, see `certbot.plugins`.

"""
import zope.interface

from certbot import interfaces
from certbot.plugins import dns_common



@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
class Authenticator(dns_common.DNSAuthenticator):
    """Example Authenticator."""

    description = "Example Authenticator plugin"

    # Implement all methods from IAuthenticator, remembering to add
    # "self" as first argument, e.g. def prepare(self)...

    def _setup_credentials(self):
        pass

    def _perform(self, domain, validation_domain_name, validation):
        pass

    def _cleanup(self, domain, validation_domain_name, validation):
        pass
