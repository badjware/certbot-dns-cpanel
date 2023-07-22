# certbot-dns-cpanel

Plugin to allow acme dns-01 authentication of a name managed in cPanel. Useful for automating and creating a Let's Encrypt certificate (wildcard or not) for a service with a name managed by cPanel, but installed on a server not managed in cPanel.

## Named Arguments
| Argument | Description |
| --- | --- |
| --cpanel-credentials &lt;file&gt; | cPanel credentials INI file **(required)** |
| --cpanel-propagation-seconds &lt;seconds&gt; | The number of seconds to wait for DNS to propagate before asking the ACME server to verify the DNS record (Default: 30) |

## Install
``` bash
pip install certbot-dns-cpanel
```

## Credentials
Download the file `credentials.ini.example` and rename it to `credentials.ini`. Edit it to set your cPanel url, username and password.
```
# The url cPanel url
# include the scheme and the port number (usually 2083 for https)
cpanel_url = https://cpanel.example.com:2083

# The cPanel username
cpanel_username = user

# The cPanel password
cpanel_password = hunter2
```

## Example
You can now run certbot using the plugin and feeding the credentials file.
For example, to get a wildcard certificate for *.example.com and example.com:
``` bash
certbot certonly \
--authenticator cpanel \
--cpanel-credentials /path/to/credentials.ini \
-d 'example.com' \
-d '*.example.com'
```

You can also specify a installer plugin with the `--installer` option:

``` bash
certbot run \
--authenticator cpanel \
--installer apache \
--cpanel-credentials /path/to/credentials.ini \
-d 'example.com' \
-d '*.example.com'
```

You may also install the certificate onto a domain on your cPanel account:

```bash
certbot run \
--authenticator cpanel \
--installer certbot-dns-cpanel:cpanel \
--cpanel-credentials /path/to/credentials.ini \
-d 'example.com' \
-d '*.example.com'
```

Depending on your provider you may need to use the `--cpanel-propagation-seconds` option to extend
the DNS propagation time.

## Docker
A docker image [badjware/certbot-dns-cpanel](https://hub.docker.com/r/badjware/certbot-dns-cpanel), based on [certbot/certbot](https://hub.docker.com/r/certbot/certbot) is provided for your convenience:
``` bash
docker run -it \
-v /path/to/credentials.ini:/tmp/credentials.ini \
badjware/certbot-dns-cpanel \
certonly \
--authenticator cpanel \
--cpanel-credentials /tmp/credentials.ini \
-d 'example.com' \
-d '*.example.com'
```

## Additional documentation
* https://documentation.cpanel.net/display/DD/Guide+to+cPanel+API+2
* https://certbot.eff.org/docs/
