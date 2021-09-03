# certbot-dns-cpanel

Plugin to allow acme dns-01 authentication of a name managed in cPanel. Useful for automating and creating a Let's Encrypt certificate (wildcard or not) for a service with a name managed by cPanel.
And to allow installing the ssl certificate on cPanel, useful if cPanel provider does not support letsencrypt / other automated ssl providers.

## Named Arguments
| Argument | Description |
| --- | --- |
| --certbot-dns-cpanel:authenticator-credentials=&lt;file&gt; | cPanel credentials INI file |
| --certbot-dns-cpanel:authenticator-propagation-seconds=&lt;seconds&gt; | The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record (Default: 30) |
| --certbot-dns-cpanel:installer-credentials=&lt;file&gt; | same as for the authenticator, pointer to the same INI file |

## Install
``` bash
pip install certbot-dns-cpanel
```

## Credentials
Download the file `credentials.ini.example` and rename it to `credentials.ini`. Edit it to set your cPanel url, username and token / password (token is the preferred method).
Unfortunately properties need to be duplicated for authenticator and installer due to the way how it is implmented by certbot.
```
# The url cPanel url
# include the scheme and the port number (usually 2083 for https)
certbot_dns_cpanel:authenticator_url = https://cpanel.exemple.com:2083
certbot_dns_cpanel:installer_url = https://cpanel.example.com:2083

# The cPanel username
certbot_dns_cpanel:authenticator_username = user
certbot_dns_cpanel:installer_username = user

# The cPanel token / password
certbot_dns_cpanel:authenticator_token = tokenvalue
certbot_dns_cpanel:installer_token = tokenvalue
```

## Exemple
You can now run certbot using the plugin and feeding the credentials file.  
For exemple, to get a wildcard certificate for *.exemple.com and exemple.com
and install it on cPanel:
``` bash
certbot \
--authenticator certbot-dns-cpanel:authenticator \
--certbot-dns-cpanel:authenticator-credentials=/path/to/credentials.ini \
--certbot-dns-cpanel:authenticator-propagation-seconds=60
--installer certbot-dns-cpanel:installer \
--certbot-dns-cpanel:installer-credentials=/pth/to/credentials.ini
-d 'exemple.com' \
-d '*.exemple.com'
```

## Docker
A docker image [badjware/certbot-dns-cpanel](https://hub.docker.com/r/badjware/certbot-dns-cpanel), based on [certbot/certbot](https://hub.docker.com/r/certbot/certbot) is provided for your convenience:
``` bash
docker run -it \
-v /path/to/credentials.ini:/tmp/credentials.ini \
badjware/certbot-dns-cpanel \
certonly \
--authenticator certbot-dns-cpanel:cpanel \
--certbot-dns-cpanel:cpanel-credentials /tmp/credentials.ini \
-d 'exemple.com' \
-d '*.exemple.com'
```

## Additional documentation
* https://documentation.cpanel.net/display/DD/Guide+to+cPanel+API+2
* https://certbot.eff.org/docs/
