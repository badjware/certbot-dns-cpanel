"""cPanel dns-01 authenticator plugin"""
import logging
import base64
import json
from urllib import request
from urllib.parse import urlencode

import zope.interface

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
        self._get_cpanel_client().add_txt_record(validation_domain_name, validation)

    def _cleanup(self, domain, validation_domain_name, validation):
        self._get_cpanel_client().del_txt_record(validation_domain_name, validation)

    def _get_cpanel_client(self):
        return _CPanelClient(
            self.credentials.conf('host'),
            self.credentials.conf('port'),
            self.credentials.conf('accountid'),
            self.credentials.conf('username'),
            self.credentials.conf('password')
        )

class _CPanelClient:

    def __init__(self, host, port, accountid, username, password):
        self.request_url = "https://%s:%s/json-api/cpanel" % (host, port)
        self.data = {
            'cpanel_jsonapi_user': username,
            'cpanel_jsonapi_apiversion': '2',
            'cpanel_jsonapi_module': 'ZoneEdit'
        }
        self.headers = {
            'Authorization': 'Basic %s' % str(base64.b64encode(bytes("%s:%s" % (username, password), "utf8")), 'utf8')
        }

    def add_txt_record(self, record_name, record_content, record_ttl=60):
        cpanel_domain, cpanel_name = self._get_domain_and_name(record_name)

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'add_zone_record'
        data['domain'] = cpanel_domain
        data['name'] = cpanel_name
        data['type'] = 'TXT'
        data['txtdata'] = record_content
        data['ttl'] = record_ttl

        logger.debug(data)
        with request.urlopen(
            request.Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers,
            )
        ) as response:
            logger.debug(response.read())

    def del_txt_record(self, record_name, record_content, record_ttl=60):
        cpanel_domain, _ = self._get_domain_and_name(record_name)
        record_lines = self._get_record_line(cpanel_domain, record_name, record_content)

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'remove_zone_record'
        data['domain'] = cpanel_domain

        # the lines get shifted when we remove one, so we reverse-sort to avoid that
        record_lines.sort(reverse=True)
        for record_line in record_lines:
            data['line'] = record_line

            with request.urlopen(
                request.Request(
                    "%s?%s" % (self.request_url, urlencode(data)),
                    headers=self.headers
                )
            ) as response:
                logger.debug(response.read())

    def _get_domain_and_name(self, record_domain):
        cpanel_domain = ''
        cpanel_name = ''

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'fetchzones'

        with request.urlopen(
            request.Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers
            )
        ) as response:
            for zone in json.load(response)['cpanelresult']['data'][0]['zones']:
                if record_domain is zone or record_domain.endswith('.' + zone):
                    cpanel_domain = zone
                    cpanel_name = record_domain[:-len(zone)-1]

        return (cpanel_domain, cpanel_name)

    def _get_record_line(self, cpanel_domain, record_name, record_content):
        record_lines = []

        data = self.data.copy()
        data['cpanel_jsonapi_func'] = 'fetchzone_records'
        data['domain'] = cpanel_domain
        data['name'] = record_name + '.' if not record_name.endswith('.') else ''
        data['type'] = 'TXT'
        data['txtdata'] = record_content

        with request.urlopen(
            request.Request(
                "%s?%s" % (self.request_url, urlencode(data)),
                headers=self.headers
            )
        ) as response:
            response_data = json.load(response)['cpanelresult']['data']
            record_lines = [int(d['line']) for d in response_data]

        return record_lines
