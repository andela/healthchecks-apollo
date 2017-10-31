from hc.api.models import Check
from hc.test import BaseTestCase
from datetime import timedelta as td
from django.utils import timezone


class UnresolvedIssuesTestCase(BaseTestCase):

    def setUp(self):
        super(UnresolvedIssuesTestCase, self).setUp()
        self.check = Check(user=self.alice, name="Alice Was Here")
        self.check.save()

    def test_unresolved_issues(self):
        self.check.last_ping = timezone.now() - td(days=3)
        self.check.status = "up"
        self.check.save()

        self.client.login(username="alice@example.org", password="password")
        r = self.client.get("/unresolved/")

        # Desktop
        self.assertContains(r, "icon-down")

        # Mobile
        self.assertContains(r, "label-danger")
