# -*- coding: utf-8 -*-

import sys

from salt.scripts import _install_signal_handlers


def salt_napalm():
    '''
    Execute a salt convenience routine.
    '''
    import salt_napalm.cli
    if '' in sys.path:
        sys.path.remove('')
    client = salt_napalm.cli.SaltNAPALM()
    _install_signal_handlers(client)
    client.run()


if __name__ == '__main__':
    salt_napalm()
