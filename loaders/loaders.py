from traceback import format_exc, format_exception, format_exception_only
from importlib import import_module
from requests import Session
from loaders.models import RequestData, ResponseData, LoaderFailure
from radio.models import Radio


def create_request_data(request):
    return RequestData.objects.create(
        method=request.method,
        url=request.url,
    )


def create_response_data(response):
    return ResponseData.objects.create(
        status_code=response.status_code,
        contents=response.content,
    )


def create_failure(radio, failure_type, request, response, ex=None, tb=None):
    error_message = "{}: {}".format(type(ex).__name__, str(ex)) if ex else ""

    print("*"*80)
    print(format_exception(ex))
    print("*"*80)
    print(format_exception_only(ex))
    print("*"*80)

    return LoaderFailure.objects.create(
        type=failure_type,
        radio=radio,
        error_message=error_message,
        request=create_request_data(request),
        response=create_response_data(response),
    )


def create_request_failure(radio, request, response):
    return create_failure(radio, LoaderFailure.TYPE_REQUEST, request, response)


def create_parse_failure(radio, request, response, exception):
    return create_failure(radio, LoaderFailure.TYPE_PARSE, request, response, exception)


def get_loader(radio_slug):
    return import_module('loaders.implementations.{}'.format(radio_slug))


def load_current_song(radio_slug):
    radio = Radio.objects.get(slug=radio_slug)
    loader = get_loader(radio_slug)

    # Fetch data
    request = loader.form_request()
    session = Session()
    response = session.send(request.prepare())

    if response.status_code >= 400:
        create_request_failure(radio, request, response)
        return None

    # Parse data
    try:
        return loader.parse_response(response)
    except Exception as ex:
        tb = format_exc()
        create_parse_failure(radio, request, response, ex, tb)
        return None
