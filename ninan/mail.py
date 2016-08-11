from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _


def send_validation(strategy, code):
    url = reverse('social:complete', args=(strategy.backend.name,)) + \
        '?verification_code=' + code.code
    host = Site.objects.get_current().domain
    full_url = 'http://%s%s' % (host, url)
    title = unicode(_('Validate your account'))
    payload = unicode(_('Please click the follow link to active your accout '
                        'at ninan.sinaapp.com .\n {0}'.format(full_url)))
    send_mail(title, payload,
              settings.EMAIL_HOST_USER,
              [code.email],
              fail_silently=False)
