# certbot-dns-cpanel

Plugin to allow acme dns-01 authentication of a name managed in cPanel. Useful for automating and creating a Let's Encrypt certificate (wildcard or not) for a service with a name managed by cPanel, but installed on a server not managed in cPanel.

## How to use
### 1. Install
First, install certbot and the plugin using pip:
```
pip install certbot certbot-dns-cpanel
```
### 2. Configure
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
### 3. Run
You can now run certbot using the plugin and feeding the credentials file.  
For exemple, to get a certificate for exemple.com and www.exemple.com:
```
certbot certonly \
--authenticator certbot-dns-cpanel:cpanel \
--certbot-dns-cpanel:panel-credentials /path/to/credentials.ini \
-d exemple.com \
-d www.exemple.com
```
To create a wildcard certificate *.exemple.com and install it on an apache server, the installer plugin must be specified with the `--installer` option.
You will need to install the apache plugin if it's not already present on your system.
```
pip install certbot-apache
certbot run \
--apache \
--authenticator certbot-dns-cpanel:cpanel \
--installer apache \
--certbot-dns-cpanel:cpanel-credentials /path/to/credentials.ini \
-d '*.exemple.com'
```
The certbot documentation has some additionnal informations about combining authenticator and installer plugins: https://certbot.eff.org/docs/using.html#getting-certificates-and-choosing-plugins

## Additional documentation
* https://documentation.cpanel.net/display/DD/Guide+to+cPanel+API+2
* https://certbot.eff.org/docs/
