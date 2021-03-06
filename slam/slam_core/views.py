"""
This module provide HTTP view for SLAM. slam_core just provide basic view like home, login, logout.
each django's App (slam_*) provide it's own view
"""
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import FieldError

from slam_domain.models import Domain, DomainEntry
from slam_network.models import Network, Address
from slam_hardware.models import Hardware, Interface
from slam_host.models import Host

from slam_core.producer import utils


@login_required
def index(request):
    """
    This is the default home page of SLAM. It will only be available through a Web browser as
    it will only return a HTTP rendering (which will need javascript support).

    :param request: a full HTTP request from user
    """
    return render(request, 'core/index.html', dict())


@ensure_csrf_cookie
def login(request):
    """
    This is the sign in form. 2 method type are supported
      - GET: to show the HTTP login page
      - POST: to trig login action

    :param request: full HTTP request from user
    """
    redirect_page = request.GET.get('next')
    if request.method == 'POST':
        user = auth.authenticate(username=request.POST.get('username'),
                                 password=request.POST.get('password'))
        if user is not None:
            auth.login(request, user)
            return JsonResponse({'next': redirect_page})
        return JsonResponse({
            'status': 'failed',
            'message': 'Authentication problem, check your login/password'
        })
    return render(request, "core/login.html", dict())


@ensure_csrf_cookie
def csrf(request):
    # As django need view to have request option but we don't need it, we need to exclude pylint
    # unused-argument for this method
    # pylint: disable=W0613
    """
    This page is only a empty page to force CSRF token to be send to browser. In case of REST API,
    CSRF can be painful to retrieve as it is not sent on every pages. This page force Django to
    resend a new CSRF Token.

    As django view are generic function with "request" as parameter and we don't use it, we must
    tell to pylint to *not* check W0613 (unused-argument) from this function.

    :param request: full HTTP request from user
    """
    return JsonResponse(dict())


@login_required
def logout(request):
    """
    This is the logout page. Whatever we provide, that trig user logout and that's all.

    :param request: full HTTP request from user
    """
    auth.logout(request)
    return HttpResponseRedirect('/')


@login_required
def search(request):
    """
    This function will return a list of objects that match the filter. We just provide basic
    filter as string filter but searching will be done on all field. If no filter has been provide
    by user, we get all object database.

    The output is a dict abstraction of object in short format (see show method from modules for
    more information)

    :param request: full HTTP request from user
    :return:
    """
    if request.method == 'GET' and request.headers['Accept'] != 'application/json':
        return render(request, 'core/search.html', dict())
    data = request.GET.dict()
    options = dict()
    for item in data:
        options['{}__contains'.format(item)] = data[item]
    try:
        domains = Domain.search(options)
    except FieldError:
        domains = []
    try:
        entries = DomainEntry.search(options)
    except FieldError:
        entries = []
    try:
        networks = Network.search(options)
    except FieldError:
        networks = []
    try:
        addresses = Address.search(options)
    except FieldError:
        addresses = []
    try:
        hardware = Hardware.search(options)
    except FieldError:
        hardware = []
    try:
        interface = Interface.search(options)
    except FieldError:
        interface = []
    try:
        hosts = Host.search(options)
    except FieldError:
        hosts = []

    result = {
        'domains': domains,
        'entries': entries,
        'networks': networks,
        'addresses': addresses,
        'hardware': hardware,
        'interface': interface,
        'hosts': hosts
    }
    return JsonResponse(result, safe=False)


@login_required
def diff(request):
    # As django need view to have request option but we don't need it, we need to exclude pylint
    # unused-argument for this method
    # pylint: disable=W0613
    """
    This function provide a git diff output. This is a raw version of git diff command so
    it can be painfull to read.

    :param request: full HTTP request from user
    :return:
    """
    result = utils.diff()
    return JsonResponse(result)


@login_required
def commit(request):
    # As django need view to have request option but we don't need it, we need to exclude pylint
    # unused-argument for this method
    # pylint: disable=W0613
    """
    This function trig DNS/DHCP and freeradius rendering. It will return a raw git diff.

    :param request: full HTTP request from user
    :return:
    """
    result = utils.commit()
    return JsonResponse(result)


@login_required
def publish(request):
    # As django need view to have request option but we don't need it, we need to exclude pylint
    # unused-argument for this method
    # pylint: disable=W0613
    """
    This function trig a git push command to publish DNS/DHCP and freeradius rendering available.

    :param request: full HTTP request from user
    :return:
    """
    result = utils.publish()
    return JsonResponse(result)


@login_required
def logs(request):
    """
    This function display slam log file into a web pages

    :param request: full HTTP request from user
    :return:
    """
    with open('./slam.log', 'r') as file:
        log_lines = file.readlines()
        reversed_lines = log_lines[::-1]
        log_file = '<br/>'.join(reversed_lines)
    return render(request, 'core/logs.html', {'logs': log_file})
