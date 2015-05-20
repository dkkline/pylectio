"""
Contains the Session object, used when dealing with Lectio endpoints
that require authentication.
"""

import requests
from bs4 import BeautifulSoup as BS
from urllib.parse import urlparse, parse_qs

from .exceptions import (NotLoggedInError, SessionClosedError,
                         AuthenticationError)
from .config import VIEW_STATEX, EVENTVALIDATION
from .urls import (make_login_url, make_frontpage_url,
                   make_assignments_overview_url)
from .assignment import Assignment


class Session(object):
    """
    A session object used for authenticating requests to lectio.
    """
    def __init__(self, school_id):
        self.school_id = school_id
        self.student_id = None

        self.session = requests.Session()
        self.authenticated = False
        self.open = True

    def assert_authenticated(self):
        """
        Raises ``NotLoggedInError`` if the ``Session`` is not authenticated.
        """
        if not self.authenticated:
            raise NotLoggedInError("You must be authenticated.")

    def assert_open(self):
        """
        Raises ``SessionClosedError`` of the ``Session`` is not open.
        """
        if not self.open:
            raise SessionClosedError("Session has already been closed.")

    def assert_any(self):
        self.assert_authenticated()
        self.assert_open()

    def auth(self, username, password):
        """
        Authenticates the ``Session`` using the credentials ``username`` and
        ``password``.
        """
        self.assert_open()

        url = make_login_url(self.school_id)

        payload = {
            "time": "0",  # Always
            "__EVENTTARGET": "m$Content$submitbtn2",  # Always
            "__EVENTARGUMENT": "",  # Always
            "__SCROLLPOSITION": "",  # Always
            "__VIEW_STATEX": VIEW_STATEX,  # Works, should be dynamic
            "__VIEWSTATE": "",  # Always
            "__EVENTVALIDATION": EVENTVALIDATION,  # Works, should be dynamic
            "m$Content$username2": username,
            "m$Content$passwordHidden": password,
            "LectioPostbackId": ""  # Always
        }

        req = self.session.post(url, data=payload, allow_redirects=True)
        self.authenticated = True

        if req.url != make_frontpage_url(self.school_id):
            raise AuthenticationError("Failed to authenticate.")

        soup = BS(req.content)

        meta_tag = soup.find("meta", attrs={"name": "msapplication-starturl"})
        frontpage_url = meta_tag["content"]

        query = urlparse(frontpage_url).query

        self.student_id = parse_qs(query)["elevid"][0]

        return True

    def close(self):
        """
        Closes the ``Session``.
        """
        self.assert_open()

        self.session.close()
        self.open = False

    def get_assignments(self):
        url = make_assignments_overview_url(self.school_id)
        
        payload = {
            "elevid": self.student_id
        }

        req = self.session.get(url, params=payload)
        soup = BS(req.content)

        table_attrs = {
            "id": "s_m_Content_Content_ExerciseGV",
            "class": "ls-table-layout1 maxW textTop"
        }

        table = soup.find("table", attrs=table_attrs)

        def _is_valid_assignment_row(tag):
            """
            Used by BeautifulSoup to determine whether a tag is a valid assignment
            row or not.
            """
            validators = []

            validators.append(tag.name == "tr")
            validators.append(tag.get("class") in (None, ["separationCell"]))

            return all(validators)

        assignment_rows = table.find_all(_is_valid_assignment_row)

        assignments = [Assignment(row) for row in assignment_rows]

        return assignments
