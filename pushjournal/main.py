import click
from systemd import journal
import re
from . import config
from . import notifiers



@click.command()
@click.option("-c", "--config-file", required=True)
def main_entry_point(config_file):
    app_config = config.load(config_file)
    app_notifiers = notifiers.create_notifiers(app_config)
    reader = journal.Reader()

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

                for notifier in app_notifiers:
                    notifier.notify(f['title'].format(*m.groups()), f['body'].format(*m.groups()))
