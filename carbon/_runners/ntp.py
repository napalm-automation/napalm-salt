"""
"""
# Import stdlib
import os
import yaml

from copy import deepcopy

# Import salt modules
import salt.client
import salt.runner
from salt.ext import six

# ----------------------------------------------------------------------------------------------------------------------
# globals
# ----------------------------------------------------------------------------------------------------------------------

_PEERS = ['']

_SERVERS = [
    '17.253.34.253',  # time.apple.com
    '40.118.103.7'  # time.windows.com
]

# ----------------------------------------------------------------------------------------------------------------------
# module properties
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# property functions
# ----------------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# helper functions -- will not be exported
# ----------------------------------------------------------------------------------------------------------------------


def _get_pillar_path():

    return __opts__['pillar_roots'].get('base')[0]


def _get_client():

    return salt.client.LocalClient(__opts__['conf_file'])


def _get_rclient():

    quiet_opts = deepcopy(__opts__)
    quiet_opts.update({'quiet': True})
    _rclient = salt.runner.RunnerClient(quiet_opts)
    return _rclient


# ----------------------------------------------------------------------------------------------------------------------
# callable functions
# ----------------------------------------------------------------------------------------------------------------------


def diff():

    """Returns the differences between the expected device config and the actual config."""

    _client = _get_client()

    ntp_state_result = _client.cmd('*', 'state.sls', ['router.ntp', 'test=True'], expr_form='glob', timeout=60)

    _ntp_diff = {
        'add': {},
        'remove': {}
    }

    for device, device_states_run in six.iteritems(ntp_state_result):
        for state_run, state_result in six.iteritems(device_states_run):
            if state_result.get('result') is False:
                continue

            state_changes = state_result.get('changes', {})
            peers_change = state_changes.get('peers', {})
            servers_change = state_changes.get('servers', {})

            add_peers = peers_change.get('added', [])
            remove_peers = peers_change.get('removed', [])

            add_servers = servers_change.get('added', [])
            remove_servers = servers_change.get('removed', [])

            if add_peers:
                if 'peers' not in _ntp_diff['add'].keys():
                    _ntp_diff['add']['peers'] = {}
                _ntp_diff['add']['peers'][device] = add_peers

            if remove_peers:
                if 'peers' not in _ntp_diff['remove'].keys():
                    _ntp_diff['remove']['peers'] = {}
                _ntp_diff['remove']['peers'][device] = remove_peers

            if add_servers:
                if 'servers' not in _ntp_diff['add'].keys():
                    _ntp_diff['add']['servers'] = {}
                _ntp_diff['add']['servers'][device] = add_servers

            if remove_servers:
                if 'servers' not in _ntp_diff['remove'].keys():
                    _ntp_diff['remove']['servers'] = {}
                _ntp_diff['remove']['servers'][device] = remove_servers

    return _ntp_diff


def unsynchronized():

    _client = _get_client()
    _rclient = _get_rclient()
    ntp_stats = _client.cmd('*', 'ntp.stats', [], expr_form='glob', timeout=120)

    _not_synced_devices = list()
    _over_stratum_devices = list()

    for device, device_ntp_stats in six.iteritems(ntp_stats):
        if not device_ntp_stats.get('result', False):
            continue
        device_ntp_stats = device_ntp_stats.get('out', {})
        if not device_ntp_stats:
            continue  # if cannot retrieve for some reason,
        kwarg={'minion': device}
        device_pillar = _rclient.cmd('pillar.show_pillar', kwarg=kwarg)
        sync = device_pillar.get('ntp', {}).get('synchronized', False)
        stratum = device_pillar.get('ntp', {}).get('stratum', 16)
        if not sync:
            continue  # if this device does not need sync
        synced_peers = [
            {peer_stats.get('remote'): peer_stats.get('stratum', 16)} \
            for peer_stats in device_ntp_stats \
            if peer_stats.get('remote', '') and peer_stats.get('synchronized', False)
        ]
        # the list of peers synchronized with
        if not synced_peers:
            _not_synced_devices.append(device)
            continue
        under_stratum = [synced_peer.keys()[0] for synced_peer in synced_peers if synced_peer.values()[0] <= stratum]
        if not under_stratum:
            _over_stratum_devices.append(device)
            continue

    return (_not_synced_devices, _over_stratum_devices)


def make_pillars_from_existing():

    _client = _get_client()
    _pillar_path = _get_pillar_path()

    ntp_peers = _client.cmd('*', 'ntp.peers', [], expr_form='glob', timeout=60)
    ntp_servers = _client.cmd('*', 'ntp.servers', [], expr_form='glob', timeout=60)

    for device, device_ntp_peers in six.iteritems(ntp_peers):
        if not device_ntp_peers.get('result', False):
            continue
        ntp_peers_list = device_ntp_peers.get('out', [])
        ntp_servers_list = ntp_servers.get(device, {}).get('out', [])
        ntp_filecontent = {
            'ntp.peers': ntp_peers_list,
            'ntp.servers': ntp_servers_list
        }
        device_flat_name = device.replace('.', '_')
        ntp_filename = 'ntp_{device}.sls'.format(
            device=device_flat_name
        )
        ntp_peers_filepath = os.path.join(_pillar_path, ntp_filename)
        with open(ntp_peers_filepath, 'w') as ntp_file:
            ntp_file.write(
                yaml.dump(ntp_filecontent, default_flow_style=False)
            )


def rebuild_pillars():

    _pillar_path = _get_pillar_path()

    ntp_files = [f for f in os.listdir(_pillar_path) if os.path.isfile(os.path.join(_pillar_path, f)) and f.startswith('ntp_')]

    ntp_file_content = {
        'ntp.peers': _PEERS,
        'ntp.servers': _SERVERS
    }

    for ntp_filename in ntp_files:
        with open(ntp_filename, 'w') as ntp_file:
            ntp_file.write(
                yaml.dump(ntp_file_content, default_flow_style=False)
            )
