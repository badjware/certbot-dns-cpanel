"""cPanel dns-01 authenticator plugin"""
import logging
import base64
import json

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
from certbot.plugins import dns_common


logger = logging.getLogger(__name__)

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
    def add_parser_arguments(cls, add): # pylint: disable=arguments-differ
        super(Authenticator, cls).add_parser_arguments(add, default_propagation_seconds=10)
        add("credentials",
            type=str,
            help="The cPanel credentials INI file")

    def more_info(self): # pylint: disable=missing-docstring
        return self.description

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

    def _setup_credentials(self):
        self.credentials = self._configure_credentials(
            'credentials',
            'The cPanel credentials INI file',
            None,
            self._validate_credentials
        )

    def _perform(self, domain, validation_domain_name, validation):
        self._get_cpanel_client().add_txt_record(validation_domain_name, validation)

    def _cleanup(self, domain, validation_domain_name, validation):
        self._get_cpanel_client().del_txt_record(validation_domain_name, validation)

    def _get_cpanel_client(self):
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

class _CPanelClient:
    """Encapsulate communications with the cPanel API 2"""
    def __init__(self, url, username, password, token):
        self.request_url = "%s/json-api/cpanel" % url
        self.data = {
            'cpanel_jsonapi_user': username,
            'cpanel_jsonapi_apiversion': '2',
            'cpanel_jsonapi_module': 'ZoneEdit'
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

    def add_txt_record(self, record_name, record_content, record_ttl=60):
        """Add a TXT record
        :param str record_name: the domain name to add
        :param str record_content: the content of the TXT record to add
        :param int record_ttl: the TTL of the record to add
        """
        cpanel_zone, cpanel_name = self._get_zone_and_name(record_name)

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'add_zone_record'
        data['domain'] = cpanel_zone
        data['name'] = cpanel_name
        data['type'] = 'TXT'
        data['txtdata'] = record_content
        data['ttl'] = record_ttl

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers,
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        if response_data['data'][0]['result']['status'] == 1:
            logger.info("Successfully added TXT record for %s", record_name)
        else:
            raise errors.PluginError("Error adding TXT record: %s" % response_data['data'][0]['result']['statusmsg'])

    def del_txt_record(self, record_name, record_content, record_ttl=60):
        """Remove a TXT record
        :param str record_name: the domain name to remove
        :param str record_content: the content of the TXT record to remove
        :param int record_ttl: the TTL of the record to remove
        """
        cpanel_zone, _ = self._get_zone_and_name(record_name)

        record_lines = self._get_record_line(cpanel_zone, record_name, record_content, record_ttl)

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'remove_zone_record'
        data['domain'] = cpanel_zone

        # the lines get shifted when we remove one, so we reverse-sort to avoid that
        record_lines.sort(reverse=True)
        for record_line in record_lines:
            data['line'] = record_line

            response = urlopen(
                Request(
                    "%s?%s" % (self.request_url, urlencode(data)),
                    headers=self.headers
                )
            )
            response_data = json.load(response)['cpanelresult']
            logger.debug(response_data)
            if response_data['data'][0]['result']['status'] == 1:
                logger.info("Successfully removed TXT record for %s", record_name)
            else:
                raise errors.PluginError("Error removing TXT record: %s" % response_data['data'][0]['result']['statusmsg'])

    def _get_zone_and_name(self, record_domain):
        """Find a suitable zone for a domain
        :param str record_name: the domain name
        :returns: (the zone, the name in the zone)
        :rtype: tuple
        """
        cpanel_zone = ''
        cpanel_name = ''

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'fetchzones'

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        matching_zones = {zone for zone in response_data['data'][0]['zones'] if record_domain == zone or record_domain.endswith('.' + zone)}
        if matching_zones:
            cpanel_zone = max(matching_zones, key = len)
            cpanel_name = record_domain[:-len(cpanel_zone)-1]
        else:
            raise errors.PluginError("Could not get the zone for %s. Is this name in a zone managed in cPanel?" % record_domain)

        return (cpanel_zone, cpanel_name)

    def _get_record_line(self, cpanel_zone, record_name, record_content, record_ttl):
        """Find the line numbers of a record a zone
        :param str cpanel_zone: the zone of the record
        :param str record_name: the name in the zone of the record
        :param str record_content: the content of the record
        :param str cpanel_ttl: the ttl of the record
        :returns: the line number and all it's duplicates
        :rtype: list
        """
        record_lines = []

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'fetchzone_records'
        data['domain'] = cpanel_zone
        data['name'] = record_name + '.' if not record_name.endswith('.') else ''
        data['type'] = 'TXT'
        data['txtdata'] = record_content
        data['ttl'] = record_ttl

        response = urlopen(
            Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers
            )
        )
        response_data = json.load(response)['cpanelresult']
        logger.debug(response_data)
        record_lines = [int(d['line']) for d in response_data['data']]

        return record_lines

# vim: set ts=4 sw=4:
