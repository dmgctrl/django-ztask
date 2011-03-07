from django.core.management.base import BaseCommand
from django.utils import autoreload
#
from ztask.conf import settings
#
from optparse import make_option
import sys
import zmq
import traceback
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True, help='Tells Django to NOT use the auto-reloader.'),
    )
    args = ''
    help = 'Start the ztaskd server'
 
    def handle(self, *args, **options):
        use_reloader = options.get('use_reloader', True)
        if use_reloader:
            autoreload.main(self._handle)
        else:
            self._handle()

    def _handle(self):
        context = zmq.Context()
        socket = context.socket(zmq.UPSTREAM)
        socket.setsockopt(zmq.HWM, 64)
        socket.bind(settings.ZTASKD_URL)

        print "ztaskd development server started on %s." % (settings.ZTASKD_URL)
        cache = {}
        while True:
            try:
                (function_name, args, kwargs) = socket.recv_pyobj() 
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
                traceback.print_exc(e)
