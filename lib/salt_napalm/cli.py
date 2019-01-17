# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from salt_napalm.parsers import SaltNAPALMOptionParser

import os
import salt.runner
import salt.utils.parsers
from salt.utils.verify import check_user, verify_log
from salt.exceptions import SaltClientError
from salt.ext import six
import salt.defaults.exitcodes  # pylint: disable=W0611

try:
    from salt.utils import output_profile
    from salt.utils import activate_profile
except ImportError:
    from salt.utils.profile import output_profile
    from salt.utils.profile import activate_profile


class SaltNAPALM(SaltNAPALMOptionParser):
    '''
    Used to execute Salt functions on a number of devices.
    '''
    def run(self):
        '''
        Execute salt-run
        '''
        self.parse_args()

        # Setup file logging!
        self.setup_logfile_logger()
        verify_log(self.config)
        profiling_enabled = self.options.profiling_enabled
        tgt = self.config['tgt']
        fun = self.config['fun']
        args = self.config['arg']
        curpath = os.path.dirname(os.path.realpath(__file__))
        saltenv = self.config.get('saltenv', 'base')
        file_roots = self.config.get('file_roots', {saltenv: []})
        file_roots[saltenv].append(curpath)
        runner_dirs = self.config.get('runner_dirs', [])
        runner_path = os.path.join(curpath, '_runners')
        runner_dirs.append(runner_path)
        self.config['file_roots'] = file_roots
        self.config['runner_dirs'] = runner_dirs
        self.config['fun'] = 'napalm.execute'
        kwargs = {}
        tmp_args = args[:]
        for index, arg in enumerate(tmp_args):
            if isinstance(arg, dict) and '__kwarg__' in arg:
                args.pop(index)
                kwargs = arg
        kwargs['__kwarg__'] = True
        self.config['fun'] = 'napalm.execute'
        tgt_types = ('list', 'grain', 'grain_pcre', 'nodegroup')
        kwargs['tgt_type'] = 'glob'
        for tgt_type in tgt_types:
            if getattr(self.options, tgt_type):
                kwargs['tgt_type'] = tgt_type
        kwargs_opts = ('preview_target', 'batch_size', 'cache_grains',
                       'cache_pillar', 'roster', 'target_details',
                       'timeout', 'with_pillar', 'with_grains', 'sync')
        for kwargs_opt in kwargs_opts:
            if getattr(self.options, kwargs_opt) is not None:
                kwargs[kwargs_opt] = getattr(self.options, kwargs_opt)
        if getattr(self.options, 'no_cached_grains'):
            kwargs['use_cached_grains'] = False
        if getattr(self.options, 'no_cached_pillar'):
            kwargs['use_cached_pillar'] = False
        kwargs['events'] = False
        kwargs['args'] = args
        self.config['arg'] = [tgt, fun, kwargs]
        runner = salt.runner.Runner(self.config)
        if self.options.doc:
            runner.print_docs()
            self.exit(salt.defaults.exitcodes.EX_OK)

        # Run this here so SystemExit isn't raised anywhere else when
        # someone tries to use the runners via the python API
        try:
            if check_user(self.config['user']):
                pr = activate_profile(profiling_enabled)
                try:
                    ret = runner.run()
                    # In older versions ret['data']['retcode'] was used
                    # for signaling the return code. This has been
                    # changed for the orchestrate runner, but external
                    # runners might still use it. For this reason, we
                    # also check ret['data']['retcode'] if
                    # ret['retcode'] is not available.
                    if isinstance(ret, dict) and 'retcode' in ret:
                        self.exit(ret['retcode'])
                    elif isinstance(ret, dict) and 'retcode' in ret.get('data', {}):
                        self.exit(ret['data']['retcode'])
                finally:
                    output_profile(
                        pr,
                        stats_path=self.options.profiling_path,
                        stop=True)

        except SaltClientError as exc:
            raise SystemExit(six.text_type(exc))
