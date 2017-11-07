import json
from datetime import timedelta as td
from django.utils.timezone import now
from django.conf import settings
from hc.api.models import Check
from hc.test import BaseTestCase


class ListChecksTestCase(BaseTestCase):

    def setUp(self):
        super(ListChecksTestCase, self).setUp()

        self.now = now().replace(microsecond=0)

        self.a1 = Check(user=self.alice, name="Alice 1")
        self.a1.timeout = td(seconds=3600)
        self.a1.grace = td(seconds=900)
        self.a1.last_ping = self.now
        self.a1.n_pings = 1
        self.a1.status = "new"
        self.a1.save()

        self.a2 = Check(user=self.alice, name="Alice 2")
        self.a2.timeout = td(seconds=86400)
        self.a2.grace = td(seconds=3600)
        self.a2.last_ping = self.now
        self.a2.status = "up"
        self.a2.save()

    def get(self):
        return self.client.get("/api/v1/checks/", HTTP_X_API_KEY="abc")

    def test_it_works(self):
        r = self.get()
        ### Assert the response status code
        self.assertEqual(r.status_code, 200)

        doc = r.json()
        self.assertTrue("checks" in doc)

        checks = {check["name"]: check for check in doc["checks"]}
        ### Assert the expected length of checks
        self.assertEqual(len(checks), 2)

        ### Assert the checks Alice 1 and Alice 2's timeout, grace, ping_url,
        ### status, last_ping, n_pings and pause_url

        check1 = checks["Alice 1"]
        ping_url = settings.PING_ENDPOINT + str(self.a1.code)
        last_ping = check1['last_ping'].replace('T', ' ')
        pause_url = settings.SITE_ROOT + "/api/v1/checks/" + str(
            self.a1.code) + '/pause'

        # assert Alice 1 attributes
        self.assertEqual(check1['timeout'], 3600)
        self.assertEqual(check1['grace'], 900)
        self.assertEqual(check1['status'], 'new')
        self.assertEqual(check1['n_pings'], 1)
        self.assertEqual(check1['ping_url'], ping_url)
        self.assertEqual(check1['pause_url'], pause_url)
        self.assertEqual(last_ping, str(self.now))

        check2 = checks["Alice 2"]
        ping_url2 = settings.PING_ENDPOINT + str(self.a2.code)
        last_ping2 = check2['last_ping'].replace('T', ' ')
        pause_url2 = settings.SITE_ROOT + "/api/v1/checks/" + str(
            self.a2.code) + '/pause'

        # assert Alice 2 attributes
        self.assertEqual(check2['timeout'], 86400)
        self.assertEqual(check2['grace'], 3600)
        self.assertEqual(check2['status'], 'up')
        self.assertEqual(check2['n_pings'], 0)
        self.assertEqual(check2['ping_url'], ping_url2)
        self.assertEqual(check2['pause_url'], pause_url2)
        self.assertEqual(last_ping2, str(self.now))

    def test_it_shows_only_users_checks(self):
        bobs_check = Check(user=self.bob, name="Bob 1")
        bobs_check.save()

        r = self.get()
        data = r.json()
        self.assertEqual(len(data["checks"]), 2)
        for check in data["checks"]:
            self.assertNotEqual(check["name"], "Bob 1")

    ### Test that it accepts an api_key in the request
    def test_it_accepts_api_key_in_request(self):
        # test wrong api key in request
        r = self.client.get("/api/v1/checks/", HTTP_X_API_KEY="df567")
        self.assertEqual(r.status_code, 400)

        # test correct api key in request
        r = self.client.get("/api/v1/checks/", HTTP_X_API_KEY="abc")
        self.assertEqual(r.status_code, 200)
