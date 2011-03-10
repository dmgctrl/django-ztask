from django.conf import settings

ZTASKD_URL = getattr(settings, 'ZTASKD_URL', 'tcp://127.0.0.1:5555')
ZTASKD_ALWAYS_EAGER = getattr(settings, 'ZTASKD_ALWAYS_EAGER', False)
ZTASKD_DISABLED = getattr(settings, 'ZTASKD_DISABLED', False)

