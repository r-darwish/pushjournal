import socket
import json
import requests
from smtplib import SMTP
from . import config


class Notifier(object):
    def notify(self, title, message):
        raise NotImplementedError()


class Pushbullet(Notifier):
    PUSH_URL = "https://api.pushbullet.com/v2/pushes"

    def __init__(self, key, prepend_hostname):
        self._session = requests.Session()
        self._session.auth = (key, "")
        self._session.headers.update({'Content-Type': 'application/json'})
        self._prepend_hostname = prepend_hostname

    def notify(self, title, message):
        if self._prepend_hostname:
            title = "{} - {}".format(socket.gethostname(), title)

        data = {"type": "note", "title": title, "body": message}
        r = self._session.post(self.PUSH_URL, data=json.dumps(data))
        r.raise_for_status()


class Smtp(Notifier):
    def __init__(self, smtp_host, smtp_port, username, password, use_tls, from_addr, to_addrs):
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._username = username
        self._password = password
        self._use_tls = use_tls
        self._from_addr = from_addr
        self._to_addrs = to_addrs

    def notify(self, title, message):
        mailserver = SMTP(self._smtp_host, self._smtp_port)
        if self._use_tls:
            mailserver.starttls()

        if self._username:
            mailserver.login(self._username, self._password)

        message = "From: {from_addr}\nTo:{to}\nSubject:{title}\n{message}".format(
            from_addr=self._from_addr, to=", ".join(self._to_addrs), title=title, message=message)

        mailserver.sendmail(self._from_addr, self._to_addrs, message)
        mailserver.quit()


def create_notifiers(app_config):
    notifiers = []
    for n in app_config['notifiers']:
        if "type" not in n:
            raise config.ConfigError("Missing notifer type")
        if n["type"] == "pushbullet":
            if "key" not in n:
                raise config.ConfigError("Missing key for Pushbullet notifier")
            notifiers.append(Pushbullet(n['key'], n.get('prepend_hostname', False)))
        elif n["type"] == "smtp":
            for required in ["host", "from", "to"]:
                if required not in n:
                    raise config.ConfigError("\"{}\" is a required value for SMTP notifier")
            notifiers.append(Smtp(
                n['host'],
                int(n.get('port', 25)),
                n.get("user"),
                n.get("password"),
                n.get("use_tls", False),
                n['from'],
                n['to']))
        else:
            raise config.ConfigError("Unknown notifer type {}".format(n['type']))

    return notifiers
