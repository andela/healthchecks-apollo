from django.test import Client, TestCase

from hc.api.models import Check, Notification, Ping

class FrequentPingTestCase(TestCase):

    def setUp(self):
        super(FrequentPingTestCase, self).setUp()
        self.check = Check.objects.create()

    def test_check_status(self):
        r = self.client.get("/ping/%s/" % self.check.code)
        self.assertEqual(200, r.status_code)

        self.check.refresh_from_db()
        self.assertEqual("up", self.check.status)

        r_2 = self.client.get("/ping/%s/" % self.check.code)
        self.assertEqual(200, r_2.status_code)

        self.check.refresh_from_db()
        self.assertTrue(self.check.run_too_often)

    def test_sends_ping(self):
        r = self.client.get("/ping/%s/" % self.check.code)
        self.assertEqual(200, r.status_code)

        self.check.refresh_from_db()
        self.assertEqual("up", self.check.status)

        r_2 = self.client.get("/ping/%s/" % self.check.code)
        self.assertEqual(200, r_2.status_code)

        ping = Ping.objects.latest("id")
        self.assertEqual(self.check.id, ping.owner_id)

        
