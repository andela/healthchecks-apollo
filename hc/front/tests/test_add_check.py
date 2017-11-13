from hc.api.models import Check
from hc.test import BaseTestCase


class AddCheckTestCase(BaseTestCase):

    def test_it_works(self):
        url = "/checks/add/"
        self.client.login(username="alice@example.org", password="password")
        r = self.client.post(url)
        self.assertRedirects(r, "/checks/")
        assert Check.objects.count() == 1

    ### Test that team access works
    def test_team_access(self):
        url = "/checks/add/"
        self.client.login(username="alice@example.org", password="password")
        self.client.post(url)
        check_code = Check.objects.filter(user=self.alice).first().code
        self.client.logout()
        self.client.login(username="bob@example.org", password="password")
        r = self.client.get('/checks/')
        self.assertIn(str(check_code), str(r.content))
