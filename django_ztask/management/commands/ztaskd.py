from django.core.management.base import BaseCommand
from django.utils import autoreload
#
from django_ztask.models import *
#
from django_ztask.conf import settings
from django_ztask.context import shared_context as context
#
import zmq
from zmq.eventloop import ioloop
try:
    from zmq import PULL
except:
    from zmq import UPSTREAM as PULL
#
from optparse import make_option
import sys
import traceback

import logging
import pickle
import datetime
 
class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--noreload', action='store_false', dest='use_reloader', default=True, help='Tells Django to NOT use the auto-reloader.'),
        make_option('-f', '--logfile', action='store', dest='logfile', default=None, help='Tells ztaskd where to log information. Leaving this blank logs to stderr'),
        make_option('-l', '--loglevel', action='store', dest='loglevel', default='info', help='Tells ztaskd what level of information to log'),
        make_option('--replayfailed', action='store_true', dest='replay_failed', default=False, help='Replays all failed calls in the db'),
    )
    args = ''
    help = 'Start the ztaskd server'
    func_cache = {}
    
    def handle(self, *args, **options):
        self._setup_logger(options.get('logfile', None), options.get('loglevel', 'info'))
        use_reloader = options.get('use_reloader', True)
        replay_failed = options.get('replay_failed', False)
        if use_reloader:
            autoreload.main(lambda: self._handle(use_reloader, replay_failed))
        else:
            self._handle(use_reloader, replay_failed)
    
    def _handle(self, use_reloader, replay_failed):
        self.logger.info("%sServer starting on %s." % ('Development ' if use_reloader else '', settings.ZTASKD_URL))

        socket = context.socket(PULL)
        socket.bind(settings.ZTASKD_URL)
        
        io_loop = ioloop.IOLoop.instance()
        
        def _queue_handler(socket, *args, **kwargs):
            try:
                (function_name, args, kwargs, after) = socket.recv_pyobj()
                if function_name == 'ztask_log':
                    self.logger.warn('%s: %s' % (args[0], args[1]))
                    return
                task = Task.objects.create(
                    function_name=function_name, 
                    args=pickle.dumps(args), 
                    kwargs=pickle.dumps(kwargs), 
                    retry_count=settings.ZTASKD_RETRY_COUNT,
                    next_attempt=time.time() + after
                )
                
                if after:
                    ioloop.DelayedCallback(lambda: self._call_function(task.pk, function_name=function_name, args=args, kwargs=kwargs), after * 1000, io_loop=io_loop).start()
                else:
                    self._call_function(task.pk, function_name=function_name, args=args, kwargs=kwargs)
            except Exception, e:
                self.logger.error('Error setting up function. Details:\n%s' % e)
                traceback.print_exc(e)
        
        # Reload tasks if necessary
        if replay_failed:
            replay_tasks = Task.objects.all()
        else:
            replay_tasks = Task.objects.filter(failed__isnull=True)
        for task in replay_tasks:
            if task.next_attempt < time.time():
                ioloop.DelayedCallback(lambda: self._call_function(task.pk), 5000, io_loop=io_loop).start()
            else:
                after = task.next_attempt - time.time()
                ioloop.DelayedCallback(lambda: self._call_function(task.pk), after * 1000, io_loop=io_loop).start()
        
        io_loop.add_handler(socket, _queue_handler, io_loop.READ)
        io_loop.start()
    
    def p(self, txt):
        print txt
    
    def _call_function(self, task_id, function_name=None, args=None, kwargs=None):
        try:
            if not function_name:
                try:
                    task = Task.objects.get(pk=task_id)
                    function_name = task.function_name
                    args = pickle.loads(str(task.args))
                    kwargs = pickle.loads(str(task.kwargs))
                except Exception, e:
                    self.logger.info('Count not get task with id %s:\n%s' % (task_id, e))
                    return
                
            self.logger.info('Calling %s' % function_name)
            self.logger.info('Task ID: %s' % task_id)
            try:
                function = self.func_cache[function_name]
            except KeyError:
                parts = function_name.split('.')
                module_name = '.'.join(parts[:-1])
                member_name = parts[-1]
                if not module_name in sys.modules:
                    __import__(module_name)
                function = getattr(sys.modules[module_name], member_name)
                self.func_cache[function_name] = function
            function(*args, **kwargs)
            self.logger.info('Called %s successfully' % function_name)
            Task.objects.get(pk=task_id).delete()
        except Exception, e:
            self.logger.error('Error calling %s. Details:\n%s' % (function_name, e))
            task = Task.objects.get(pk=task_id)
            if task.retry_count > 0:
                task.retry_count = task.retry_count - 1
                task.next_attempt = datetime.datetime.now() + datetime.timedelta(seconds=settings.ZTASKD_RETRY_AFTER)
                # TODO: SETUP RETRY ON HEAP
                
            task.failed = datetime.datetime.now()
            task.last_exception = '%s' % e
            task.save()
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
    

