"""certbot-dns-cpanel installer plugin"""

import logging
import json
from configobj import ConfigObj

try:
    # python 3
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode
except ImportError:
    # python 2
    from urllib import urlencode
    from urllib2 import urlopen, Request

import zope.interface

from certbot import errors
from certbot import interfaces
from certbot.plugins import common
from certbot.plugins import dns_common

logger = logging.getLogger(__name__)

@zope.interface.implementer(interfaces.IInstaller)
@zope.interface.provider(interfaces.IPluginFactory)
class Installer(common.Plugin):

    description = "Upload generated certificate in cPanel"
    
    def __init__(self, *args, **kwargs):
        super(Installer, self).__init__(*args, **kwargs)

    @classmethod
    def add_parser_arguments(cls, add):
        super(Installer, cls).add_parser_arguments(add)
        add("credentials", help="The cPanel credentials INI file")

    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return self.description

    def get_all_names(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def _validate_credentials(self, credentials):
        url = credentials.conf('url')
        username  = credentials.conf('username')
        token = credentials.conf('token')
        password = credentials.conf('password')

        if not url:
            raise errors.PluginError('%s: url is required' % credentials.confobj.filename)

        if not username:
            raise errors.PluginError('%s: username and token (prefered) or password are required' % credentials.confobj.filename)

        if token:
            if password:
                logger.warning('%s: token and password are exclusive, token will be used when both are provided' % credentials.confobj.filename)
        elif not password:
            raise errors.PluginError('%s: password or token (prefered) are required' % credentials.confobj.filename)

    def _get_cpanel_client(self):
        logger.debug("Credentials file: '%s'", self.conf('credentials'))
        dnsauth = dns_common.DNSAuthenticator(self.config, __name__)
        dnsauth.dest = self.dest
        self.credentials = dnsauth._configure_credentials(
            'credentials',
            'The cPanel credentials INI file',
            None,
            self._validate_credentials
        )
        
        if not self.credentials:
            raise errors.Error('No auth data')

        if self.credentials.conf('token'):
            return _CPanelClient(self.credentials.conf('url'), self.credentials.conf('username'), None, self.credentials.conf('token'))
        elif self.credentials.conf('password'):
            return _CPanelClient(self.credentials.conf('url'), self.credentials.conf('username'), self.credentials.conf('password'), None)

        return _CPanelClient(
            self.credentials.conf('url'),
            self.credentials.conf('username'),
            self.credentials.conf('password'),
            self.credentials.conf('token'),
        )

    def deploy_cert(self, domain, cert_path, key_path, chain_path, fullchain_path):
        self._get_cpanel_client().deploy_cert(domain, cert_path, key_path, chain_path, fullchain_path, self)

    def enhance(self, domain, enhancement, options=None):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def supported_enhancements(self):  # pylint: disable=missing-docstring,no-self-use
        return []  # pragma: no cover

    def get_all_certs_keys(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def save(self, title=None, temporary=False):  # pylint: disable=no-self-use
	# this could be useful to locally keep a list of certificates installed and then clean up old ones for the same domain on servers
	# however cpanel does not seem to have an api to delete certificates
	# and, cpanel seems to not duplicate if the same certificate is installed
        pass  # pragma: no cover

    def rollback_checkpoints(self, rollback=1):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def recovery_routine(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def view_config_changes(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def config_test(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def restart(self):  # pylint: disable=missing-docstring,no-self-use
        pass  # pragma: no cover

    def renew_deploy(self, lineage, *args, **kwargs): # pylint: disable=missing-docstring,no-self-use
        """
        Renew certificates when calling `certbot renew`
        """
        # Run deploy_cert with the lineage params
        self.deploy_cert(lineage.names()[0], lineage.cert_path, lineage.key_path, lineage.chain_path, lineage.fullchain_path)

        return

class _CPanelClient:
    """Encapsulate communications with the cPanel API 2"""
    def __init__(self, url, username, password, token):
        self.request_url = "%s/json-api/cpanel" % url
        self.data = {
            'cpanel_jsonapi_user': username,
            'cpanel_jsonapi_apiversion': '2',
            'cpanel_jsonapi_module': 'SSL'
        }

        if token:
            self.headers = {
                'Authorization': 'cpanel %s:%s' % (username, token)
            }
        else:
            self.headers = {
                'Authorization': 'Basic %s' % base64.b64encode(
                ("%s:%s" % (username, password)).encode()).decode('utf8')
            }

    def deploy_cert(self, domain,  cert_path, key_path, chain_path, fullchain_path, Installer):
        """Deploy cert
        :param str domain: the domain name to upload to
        :param str cert_path: pointer to file of the cert
        :param int key_path: pointer to file of the key
        :param str chain_path: pointer to file of the chain
        :param str fullchain_path: pointer to file of the fullchain
        """

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'installssl'
        data['domain'] = domain
        data['crt'] = open(cert_path).read()
        data['key'] = open(key_path).read()


        logger.debug("req installssl: url='%s', data='%s'" % (self.request_url, urlencode(data) ) )
        
        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers,
            )
        )
        response_data = json.load(response)['cpanelresult']
        
        logger.debug("rsp innstallssl: data='%s'" % json.dumps(response_data, indent=4))
        
        if response_data['data'][0]['result'] == 1:
            logger.info("Successfully added SSL certificate for %s", domain)
        else:
            raise errors.PluginError("Error adding SSL certificate : %s" % response_data['data'][0]['output'])

interfaces.RenewDeployer.register(Installer)
