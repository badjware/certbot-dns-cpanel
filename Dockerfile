FROM certbot/certbot:v1.3.0
COPY . /certbot-dns-cpanel
RUN pip install -e /certbot-dns-cpanel

