# Pushjournal
systemd's journal is awesome. Wouldn't it be more awesome if it could send push notifications?

Pushjournal is a daemon that listens for the systemd's journal and sends push notifications based on filters that you specify. Currently is supports sending push notification throws SMTP or [Pushbullet](https://www.pushbullet.com/).

## Installation

    # pip install pushjournal

## Usage
See `examples/pushjournal.yml` for an example of a configuration file. There are two subcommands to help testing your configuration:
1. `pushjournal test_notifiers -c path_to_config` will try to send a test message through all of your notifiers.
2. `pushjournal test_filters -c path_to_config` will run through your journal history and print entries matching your filters.

Once your configuration is set you can run `pushjournal run -c path_to_config` and wait for push notifications.

You can also check out `examples/pushjournal.service` for a systemd unit file.
