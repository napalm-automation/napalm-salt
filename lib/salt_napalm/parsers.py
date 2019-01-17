# -*- coding: utf-8 -*-

import logging
import optparse

from salt.ext import six
import salt.utils.args
import salt.utils.parsers
import salt.config as config


class SaltNAPALMOptionParser(six.with_metaclass(salt.utils.parsers.OptionParserMeta,
                                                salt.utils.parsers.OptionParser,
                                                salt.utils.parsers.ConfigDirMixIn,
                                                salt.utils.parsers.MergeConfigMixIn,
                                                salt.utils.parsers.TimeoutMixIn,
                                                salt.utils.parsers.LogLevelMixIn,
                                                salt.utils.parsers.HardCrashMixin,
                                                salt.utils.parsers.SaltfileMixIn,
                                                salt.utils.parsers.TargetOptionsMixIn,
                                                salt.utils.parsers.OutputOptionsMixIn,
                                                salt.utils.parsers.ArgsStdinMixIn,
                                                salt.utils.parsers.ProfilingPMixIn,
                                                salt.utils.parsers.EAuthMixIn,
                                                salt.utils.parsers.NoParseMixin)):

    default_timeout = 1

    description = (
        'salt-napalm is a tool to invoke arbitrary Salt functions on a group\n'
        'of network devices, connecting to them through NAPALM.'
    )

    usage = '%prog [options] <target> <function> [arguments]'

    # ConfigDirMixIn config filename attribute
    _config_filename_ = 'master'

    # LogLevelMixIn attributes
    _default_logging_level_ = config.DEFAULT_MASTER_OPTS['log_level']
    _default_logging_logfile_ = config.DEFAULT_MASTER_OPTS['log_file']

    def _mixin_setup(self):
        self.add_option(
            '-d', '--doc', '--documentation',
            dest='doc',
            default=False,
            action='store_true',
            help=('Display documentation for runners, pass a runner or '
                  'runner.function to see documentation on only that runner '
                  'or function.')
        )
        self.add_option(
            '--roster',
            default=False,
            help='The name of the Salt Roster to use'
        )
        self.add_option(
            '--sync',
            default=False,
            action='store_true',
            help=('Return the replies from the devices immediately they are '
                  'received, or everything at once.')
        )
        self.add_option(
            '--cache-grains',
            default=False,
            action='store_true',
            help=('Cache the collected Grains. This is going to override the '
                  'existing cached Grains.')
        )
        self.add_option(
            '--cache-pillar',
            default=False,
            action='store_true',
            help=('Cache the compiled Pillar. This is going to override the '
                  'existing cached Pillar.')
        )
        self.add_option(
            '--no-cached-grains',
            default=False,
            action='store_true',
            help='Do not use the available cached Grains (if any).'
        )
        self.add_option(
            '--no-cached-pillar',
            default=False,
            action='store_true',
            help='Do not use the available cached Pillar (if any)'
        )
        self.add_option(
            '--with-grains',
            default=False,
            action='store_true',
            help='Do not use the available cached Grains (if any).'
        )
        self.add_option(
            '--with-pillar',
            default=False,
            action='store_true',
            help='Do not use the available cached Pillar (if any)'
        )
        self.add_option(
            '--target-details',
            default=False,
            action='store_true',
            help='Provide the connection details for the matched targets'
        )
        self.add_option(
            '-b', '--batch', '--batch-size',
            default=10,
            dest='batch_size',
            help='The number of devices to connect to in parallel.'
        )
        self.add_option(
            '--preview-target',
            dest='preview_target',
            action='store_true',
            help='Show the devices expected to match the target.'
        )
        group = self.output_options_group = optparse.OptionGroup(
            self, 'Output Options', 'Configure your preferred output format.'
        )
        self.add_option_group(group)

        group.add_option(
            '--quiet',
            default=False,
            action='store_true',
            help='Do not display the results of the run.'
        )

    def _mixin_after_parsed(self):
        if self.options.doc and len(self.args) > 1:
            self.error('You can only get documentation for one function at one time')

        if self.options.list:
            try:
                if ',' in self.args[0]:
                    self.config['tgt'] = self.args[0].replace(' ', '').split(',')
                else:
                    self.config['tgt'] = self.args[0].split()
            except IndexError:
                self.exit(42, '\nCannot execute command without defining a target.\n\n')
        else:
            try:
                self.config['tgt'] = self.args[0]
            except IndexError:
                self.exit(42, '\nCannot execute command without defining a target.\n\n')

        if self.options.preview_target:
            # Insert dummy arg which won't be used
            self.args.append('not_a_valid_command')

        # Detect compound command and set up the data for it
        if self.args:
            try:
                if ',' in self.args[1]:
                    self.config['fun'] = self.args[1].split(',')
                    self.config['arg'] = [[]]
                    cmd_index = 0
                    if (self.args[2:].count(self.options.args_separator) ==
                            len(self.config['fun']) - 1):
                        # new style parsing: standalone argument separator
                        for arg in self.args[2:]:
                            if arg == self.options.args_separator:
                                cmd_index += 1
                                self.config['arg'].append([])
                            else:
                                self.config['arg'][cmd_index].append(arg)
                    else:
                        # old style parsing: argument separator can be inside args
                        for arg in self.args[2:]:
                            if self.options.args_separator in arg:
                                sub_args = arg.split(self.options.args_separator)
                                for sub_arg_index, sub_arg in enumerate(sub_args):
                                    if sub_arg:
                                        self.config['arg'][cmd_index].append(sub_arg)
                                    if sub_arg_index != len(sub_args) - 1:
                                        cmd_index += 1
                                        self.config['arg'].append([])
                            else:
                                self.config['arg'][cmd_index].append(arg)
                        if len(self.config['fun']) > len(self.config['arg']):
                            self.exit(42, 'Cannot execute compound command without '
                                          'defining all arguments.\n')
                        elif len(self.config['fun']) < len(self.config['arg']):
                            self.exit(42, 'Cannot execute compound command with more '
                                          'arguments than commands.\n')
                    # parse the args and kwargs before sending to the publish
                    # interface
                    for i in range(len(self.config['arg'])):
                        self.config['arg'][i] = salt.utils.args.parse_input(
                            self.config['arg'][i],
                            no_parse=self.options.no_parse)
                else:
                    self.config['fun'] = self.args[1]
                    self.config['arg'] = self.args[2:]
                    # parse the args and kwargs before sending to the publish
                    # interface
                    self.config['arg'] = salt.utils.args.parse_input(
                        self.config['arg'],
                        no_parse=self.options.no_parse)
            except IndexError:
                self.exit(42, '\nIncomplete options passed.\n\n')

    def setup_config(self):
        return config.client_config(self.get_config_file_path())
