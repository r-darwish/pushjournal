import os
import tempfile
import socket
from time import sleep
import re
import traceback
import click
from systemd import journal
import logbook
import netifaces
from ._compat import urlopen
from . import config
from . import notifiers


def _get_local_ips():
    for iface in netifaces.interfaces():
        for addr in netifaces.ifaddresses(iface)[netifaces.AF_INET]:
            yield iface, addr['addr']


def _get_public_ip():
    return urlopen('http://ip.42.pl/raw').read().decode("ASCII")


@click.group()
def main_entry_point():
    pass


def _notify(app_notifiers, title, body, retry):
    for notifier in app_notifiers:
        while True:
            try:
                notifier.notify(title, body)
            except socket.error:
                if not retry:
                    raise
                logbook.error("Socket error: {}", traceback.format_exc())
                sleep(5)
            else:
                break

@main_entry_point.command()
@click.option("-c", "--config-file", required=True)
def run(config_file):
    error_handler = logbook.SyslogHandler('pushjournal', level='INFO')
    error_handler.push_application()
    app_config = config.load(config_file)
    app_notifiers = notifiers.create_notifiers(app_config)
    reader = journal.Reader()
    boot_file = os.path.join(tempfile.gettempdir(), ".pushjournal-boot")

    if app_config.get("notify_boot", False) and not os.path.isfile(boot_file):
        body = ""

        if app_config.get("show_public_ip", False):
            try:
                body += "Public IP: {}\n\n".format(_get_public_ip())
            except Exception:
                logbook.error("Could not get the public IP: {}", traceback.format_exc())
                body += "Failed to get the public IP\n"

        if app_config.get("show_local_ips", False):
            try:
                body += "Local IPs:\n{}\n\n".format(
                    "\n".join("- {}: {}".format(*addr) for addr in _get_local_ips()))
            except Exception:
                logbook.error("Could not get local IPs: {}", traceback.format_exc())
                body += "Failed to get local IPs\n"

        _notify(app_notifiers, "System booted", body, True)

        with open(boot_file, "wb"):
            pass

    for f in app_config['filters']:
        f['match'] = re.compile(f['match'])

    reader.seek_tail()
    while True:
        reader.wait()
        for entry in reader:
            for f in app_config['filters']:
                m = f['match'].search(entry['MESSAGE'])
                if not m:
                    continue

                _notify(app_notifiers, f['title'].format(*m.groups()), f['body'].format(*m.groups()), False)


@main_entry_point.command()
@click.option("-c", "--config-file", required=True)
def test_filters(config_file):
    app_config = config.load(config_file)
    reader = journal.Reader()

    for f in app_config['filters']:
        f['match'] = re.compile(f['match'])

    while True:
        for entry in reader:
            for f in app_config['filters']:
                m = f['match'].search(entry['MESSAGE'])
                if not m:
                    continue

                print("Title: {}\nMessage:{}\n".format(f['title'].format(*m.groups()), f['body'].format(*m.groups())))


@main_entry_point.command()
@click.option("-c", "--config-file", required=True)
def test_notifiers(config_file):
    app_config = config.load(config_file)
    app_notifiers = notifiers.create_notifiers(app_config)
    _notify(app_notifiers, "This is a test message", "This is the message body", True)
