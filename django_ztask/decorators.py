from django.utils.decorators import available_attrs
from functools import wraps

import logging
import types

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
            after = kwargs.pop('__ztask_after', 0)
            if settings.ZTASKD_DISABLED:
                try:
                    socket.send_pyobj(('ztask_log', ('Would have called but ZTASKD_DISABLED is True', function_name), None, 0))
                except:
                    logger.info('Would have sent %s but ZTASKD_DISABLED is True' % function_name)
                return
            elif settings.ZTASKD_ALWAYS_EAGER:
                logger.info('Running %s in ZTASKD_ALWAYS_EAGER mode' % function_name)
                if after > 0:
                    logger.info('Ignoring timeout of %d seconds because ZTASKD_ALWAYS_EAGER is set' % after)
                func(*args, **kwargs)
            else:
                try:
                    socket.send_pyobj((function_name, args, kwargs, after))
                except Exception, e:
                    if after > 0:
                        logger.info('Ignoring timeout of %s seconds because function is being run in-process' % after)
                    func(*args, **kwargs)

        def _func_delay(*args, **kwargs):
            try:
                socket.send_pyobj(('ztask_log', ('.delay is depricated... use.async instead', function_name), None, 0))
            except:
                pass
            _func(*args, **kwargs)
            
        def _func_after(*args, **kwargs):
            try:
                after = args[0]
                if type(after) != types.IntType:
                    raise TypeError('The first argument of .after must be an integer representing seconds to wait')
                kwargs['__ztask_after'] = after
                _func(*args[1:], **kwargs)
            except Exception, e:
                logger.info('Error adding delayed task:\n%s' % e)
        
        setattr(func, 'async', _func)
        setattr(func, 'delay', _func_delay)
        setattr(func, 'after', _func_after)
        return func
    
    return wrapper
