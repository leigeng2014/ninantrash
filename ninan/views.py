# coding: utf-8
"""
Commen views.
"""
import base64

from django.views.generic.base import TemplateView
from django.http import HttpResponse, HttpResponseServerError
from django.conf import settings
from django.template import (RequestContext, loader, TemplateDoesNotExist)
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import Permission


def logout(request):
    auth_logout(request)
    return render_to_response('home.html', {}, RequestContext(request))


def home(request):
    if request.user.is_authenticated():
        return redirect('done')
    return render_to_response('home.html', {}, RequestContext(request))


class ContactView(TemplateView):
    template_name = 'contact.html'

    def get(self, request, *args, **kwargs):
        admin, email = settings.ADMINS[0]
        encodedEmail = base64.b64encode(email)
        context = {'email': encodedEmail}
        prefix = getattr(settings,
                         'PREFIX_PORTION_NAME',
                         'script-prefix-protion')
        prefix_protion = request.COOKIES.get(prefix, '')
        if prefix_protion:
            print prefix_protion
        return self.render_to_response(context)


class AboutView(TemplateView):
    template_name = 'about.html'


def server_error(request, template_name='500.html'):
    '''
    Reimplement of default 500 handler.
    Default handler(i.e. server_error) returns Context({}) for template render,
    instead of RequestContext to lessen the chance of additional errors. But
    when use `i18n` templatetag in a 500 template, it needs the variable
    `LANGUAGES`. So we wrote this handler to provide RequestContext for the
    500 template.
    '''
    try:
        template = loader.get_template(template_name)
    except TemplateDoesNotExist:
        return HttpResponseServerError('<h1>Server Error (500)</h1>')
    return HttpResponseServerError(template.render(RequestContext(request,
                                                                  {})))


def test(request):
    import requests
    path = requests.certs.where()
    return HttpResponse(str(path))


@login_required
def done(request):
    """Login complete view, displays user data"""
    user = request.user
    public_perms = ['add_feedfish', 'add_stone', 'add_thing',
                    'add_profile', 'change_profile']
    perms = Permission.objects.filter(codename__in=public_perms)
    for perm in perms:
        user.user_permissions.add(perm)
    user.is_staff = True
    user.save()
    return render_to_response('done.html', {
        'user': request.user,
    }, RequestContext(request))


def signup_email(request):
    return render_to_response('email_signup.html', {}, RequestContext(request))


def validation_sent(request):
    return render_to_response('validation_sent.html', {
        'email': request.session.get('email_validation_address')
    }, RequestContext(request))


def require_email(request):
    if request.method == 'POST':
        request.session['saved_email'] = request.POST.get('email')
        backend = request.session['partial_pipeline']['backend']
        return redirect('social:complete', backend=backend)
    return render_to_response('email.html', RequestContext(request))
