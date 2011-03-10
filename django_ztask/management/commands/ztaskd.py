from django.core.management.base import BaseCommand
from django.utils import autoreload
#
from django_ztask.conf import settings
from django_ztask.context import shared_context as context
#
from optparse import make_option
import sys
import zmq
import traceback

import logging
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True, help='Tells Django to NOT use the auto-reloader.'),
        make_option('-f', '--logfile', action='store', dest='logfile', default=None, help='Tells ztaskd where to log information. Leaving this blank logs to stderr'),
        make_option('-l', '--loglevel', action='store', dest='loglevel', default='info', help='Tells ztaskd what level of information to log'),
    )
    args = ''
    help = 'Start the ztaskd server'
    
    def handle(self, *args, **options):
        self._setup_logger(options.get('logfile', None), options.get('loglevel', 'info'))
        use_reloader = options.get('use_reloader', True)
        if use_reloader:
            autoreload.main(lambda: self._handle(use_reloader))
        else:
            self._handle(use_reloader)
    
    def _handle(self, use_reloader):
        self.logger.info("%sServer starting on %s." % ('Development ' if use_reloader else '', settings.ZTASKD_URL))

        socket = context.socket(zmq.PULL)
        socket.bind(settings.ZTASKD_URL)

        cache = {}
        while True:
            function_name = None
            try:
                (function_name, args, kwargs) = socket.recv_pyobj()
                if function_name == 'ztask_log':
                    self.logger.warn('%s: %s' % (args[0], args[1]))
                    continue
                self.logger.info('Calling %s' % function_name)
                try:
                    function = cache[function_name]
                except KeyError:
                    parts = function_name.split('.')
                    module_name = '.'.join(parts[:-1])
                    member_name = parts[-1]
                    if not module_name in sys.modules:
                        __import__(module_name)
                    function = getattr(sys.modules[module_name], member_name)
                    cache[function_name] = function
                function(*args, **kwargs)
            except Exception, e:
                self.logger.error('Error calling %s. Details:\n%s' % (function_name, e))
                traceback.print_exc(e)
    
    def _setup_logger(self, logfile, loglevel):
        LEVELS = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        self.logger = logging.getLogger('ztaskd')
        self.logger.setLevel(LEVELS[loglevel.lower()])
        if logfile:
            handler = logging.FileHandler(logfile, delay=True)
        else:
            handler = logging.StreamHandler()
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    

