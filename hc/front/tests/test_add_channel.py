from django.test.utils import override_settings

from hc.api.models import Channel
from hc.test import BaseTestCase


@override_settings(PUSHOVER_API_TOKEN="token", PUSHOVER_SUBSCRIPTION_URL="url")
class AddChannelTestCase(BaseTestCase):

    def test_it_adds_email(self):
        url = "/integrations/add/"
        form = {"kind": "email", "value": "alice@example.org"}

        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url, form)

        self.assertRedirects(r, "/integrations/")
        assert Channel.objects.count() == 1

    def test_it_trims_whitespace(self):
        """ Leading and trailing whitespace should get trimmed. """

        url = "/integrations/add/"
        form = {"kind": "email", "value": "   alice@example.org   "}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)

        q = Channel.objects.filter(value="alice@example.org")
        self.assertEqual(q.count(), 1)

    def test_instructions_work(self):
        self.client.login(username="alice@example.org", password="password")
        kinds = ("email", "webhook", "pd", "pushover", "hipchat", "victorops")
        for frag in kinds:
            url = "/integrations/add_%s/" % frag
            r = self.client.get(url)
            self.assertContains(r, "Integration Settings", status_code=200)

    def test_that_bad_kinds_do_not_work(self):
        """Test handling of invalid kinds"""
        self.client.login(username="alice@example.org", password="password")
        kinds = ("facebook", "google")
        for frag in kinds:
            url = "/integrations/add_%s/" % frag
            r = self.client.get(url)
            assert r.status_code == 404

    def test_team_access_works(self):
        url = "/integrations/add/"
        form = {"kind": "email", "value": "alice@example.org"}

        self.client.login(username="alice@example.org", password="password")
        self.client.post(url, form)
        channel = Channel.objects.filter(value="alice@example.org")
        url = "/integrations/%s/checks/" % channel.first().code
        self.client.logout()
        self.client.login(username="bob@example.org", password="password")
        r = self.client.get(url)
        self.assertContains(r, "Assign Checks to Channel", status_code=200)
