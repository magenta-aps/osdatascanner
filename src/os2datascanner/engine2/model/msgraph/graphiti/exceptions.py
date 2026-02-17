# Part of the OSdatascanner system, copyright © 2014-2026 Magenta ApS.
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, you can
# obtain one at http://mozilla.org/MPL/2.0/.

"""
Custom Exceptions for error handling in graphiti.
"""


class InvalidMSGraphURLError(BaseException):
    '''
    Exception for indicating that a URL points to an
    invalid endpoint when trying to build the URL string.
    '''


class DuplicateODataParameterError(BaseException):
    '''
    Exception for handling cases where a user tries to add the
    same OData Query Parameter Twice.
    '''
