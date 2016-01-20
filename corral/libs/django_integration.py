#!/usr/bin/env python
# -*- coding: utf-8 -*-

# =============================================================================
# DOCS
# =============================================================================

"""This module provide a way to steamlessy integrate your Corral pipeline
inside a django app
"""

# Based on:
#   - http://stackoverflow.com/a/6607461/2489206
#   - https://dzone.com/articles/django-excluding-some-views


# =============================================================================
# IMPORTS
# =============================================================================

from corral import db


# =============================================================================
# MIDDLEWARE
# =============================================================================

class CorralSessionMiddleware(object):
    """Allow to add a corral database session to every
    request of Django.

    """

    def process_request(self, request):
        request.corral_session = db.Session()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if view_func.func_name == "__nocorral_middleware":
            try:
                request.corral_session.close()
                delattr(request, "corral_session")
            except AttributeError:
                pass

    def process_response(self, request, response):
        try:
            session = request.corral_session
        except AttributeError:
            return response
        try:
            session.commit()
            return response
        except:
            session.rollback()
            raise

    def process_exception(self, request, exception):
        try:
            session = request.corral_session
        except AttributeError:
            return
        session.rollback()


def no_corral(f):
    """ view decorator, the sole purpose to is 'rename' the function
    '__nocorral_middleware' """
    def __nocorral_middleware(*args, **kwargs):
        return f(*args, **kwargs)
    return __nocorral_middleware
