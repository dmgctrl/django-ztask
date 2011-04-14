from django.conf import settings

ZTASKD_URL = getattr(settings, 'ZTASKD_URL', 'tcp://127.0.0.1:5555')
ZTASKD_ALWAYS_EAGER = getattr(settings, 'ZTASKD_ALWAYS_EAGER', False)
ZTASKD_DISABLED = getattr(settings, 'ZTASKD_DISABLED', False)
ZTASKD_RETRY_COUNT = getattr(settings, 'ZTASKD_RETRY_COUNT', 5)
ZTASKD_RETRY_AFTER = getattr(settings, 'ZTASKD_RETRY_AFTER', 5)

ZTASKD_ON_LOAD = getattr(settings, 'ZTASKD_ON_LOAD', ())
#ZTASKD_ON_CALL_COMPLETE = getattr(settings, 'ZTASKD_ON_COMPLETE', ())