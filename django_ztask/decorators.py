from django.utils.decorators import available_attrs
from functools import wraps


def task():
    from django_ztask.conf import settings
    import zmq
    def wrapper(func):
        function_name = '%s.%s' % (func.__module__, func.__name__)
        context = zmq.Context()
        socket = context.socket(zmq.DOWNSTREAM)
        socket.connect(settings.ZTASKD_URL)
        @wraps(func)
        def _func(*args, **kwargs):
            try:
                socket.send_pyobj((function_name, args, kwargs))
            except Exception, e:
                func(*args, **kwargs)
        setattr(func, 'async', _func)
        setattr(func, 'delay', _func)
        return func
    return wrapper
    
