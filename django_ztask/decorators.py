from django.utils.decorators import available_attrs
from functools import wraps

import logging

def task():
    from django_ztask.conf import settings
    try:
        from zmq import PUSH
    except:
        from zmq import DOWNSTREAM as PUSH
    def wrapper(func):
        function_name = '%s.%s' % (func.__module__, func.__name__)
        
        logger = logging.getLogger('ztaskd')
        logger.info('Registered task: %s' % function_name)
        
        from django_ztask.context import shared_context as context
        socket = context.socket(PUSH)
        socket.connect(settings.ZTASKD_URL)
        @wraps(func)
        def _func(*args, **kwargs):
            if settings.ZTASKD_DISABLED:
                try:
                    socket.send_pyobj(('ztask_log', ('Would have called but ZTASKD_DISABLED is True', function_name), None))
                except:
                    logger.info('Would have sent %s but ZTASKD_DISABLED is True' % function_name)
                return
            elif settings.ZTASKD_ALWAYS_EAGER:
                logger.info('Running %s in ZTASKD_ALWAYS_EAGER mode' % function_name)
                func(*args, **kwargs)
            else:
                try:
                    socket.send_pyobj((function_name, args, kwargs))
                except Exception, e:
                    func(*args, **kwargs)

        def _func_delay(*args, **kwargs):
            try:
                socket.send_pyobj(('ztask_log', ('.delay is depricated... use.async instead', function_name), None))
            except:
                pass
            _func(*args, **kwargs)
        setattr(func, 'async', _func)
        setattr(func, 'delay', _func_delay)
        return func
    
    return wrapper
