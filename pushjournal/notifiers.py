import socket
import pushbullet
from . import config


class Notifier(object):
    def notify(self, title, message):
        raise NotImplementedError()


class Pushbullet(Notifier):
    def __init__(self, key, prepend_hostname):
        self._pb = pushbullet.Pushbullet(key)
        self._prepend_hostname = prepend_hostname

    def notify(self, title, message):
        if self._prepend_hostname:
            title = "{} - {}".format(socket.gethostname(), title)

        self._pb.push_note(title, message)


def create_notifiers(app_config):
    notifiers = []
    for n in app_config['notifiers']:
        if "type" not in n:
            raise config.ConfigError("Missing notifer type")
        if n["type"] == "pushbullet":
            if "key" not in n:
                raise config.ConfigError("Missing key for Pushbullet notifier")
            notifiers.append(Pushbullet(n['key'], n.get('prepend_hostname', False)))


    return notifiers
