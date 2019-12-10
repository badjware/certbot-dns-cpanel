# certbot-dns-cpanel

Plugin to allow acme dns-01 authentication of a name managed in cPanel. Useful for automating and creating a Let's Encrypt certificate (wildcard or not) for a service with a name managed by cPanel, but installed on a server not managed in cPanel.

## Named Arguments
| Argument | Description |
| --- | --- |
| --certbot-dns-cpanel:cpanel-credentials <file> | cPanel credentials INI file **(required)** |
| --certbot-dns-cpanel:cpanel-propagation-seconds <seconds> | The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record (Default: 30) |

## Install
``` bash
pip install certbot certbot-dns-cpanel
```

## Credentials
Download the file `credentials.ini.exemple` and rename it to `credentials.ini`. Edit it to set your cPanel url, username and password.
```
# The url cPanel url
# include the scheme and the port number (usually 2083 for https)
certbot_dns_cpanel:cpanel_url = https://cpanel.exemple.com:2083

# The cPanel username
certbot_dns_cpanel:cpanel_username = user

# The cPanel password
certbot_dns_cpanel:cpanel_password = hunter2
```

## Exemple
You can now run certbot using the plugin and feeding the credentials file.  
For exemple, to get a wildcard certificate for *.exemple.com and exemple.com:
``` bash
certbot certonly \
--authenticator certbot-dns-cpanel:cpanel \
--certbot-dns-cpanel:panel-credentials /path/to/credentials.ini \
-d 'exemple.com' \
-d '*.exemple.com'
```

Tou can also specify a installer plugin with the `--installer` option.
You will need to install the apache plugin if it's not already present on your system.
``` bash
certbot run \
--authenticator certbot-dns-cpanel:cpanel \
--installer apache \
--certbot-dns-cpanel:cpanel-credentials /path/to/credentials.ini \
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
