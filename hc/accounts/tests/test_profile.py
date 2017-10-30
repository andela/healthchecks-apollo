from django.core import mail

from hc.test import BaseTestCase
from hc.accounts.models import Member
from hc.api.models import Check


class ProfileTestCase(BaseTestCase):
    def assert_mail_sent_and_content(self, subject, content):
        """
        This method asserts that an email was sent and checks the email content using the subject and content params
        :param subject: subject line of the email sent out
        :param content: the content in the body
        :return: none
        """
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, subject)
        self.assertIn(content, mail.outbox[0].body)

    def test_it_sends_set_password_link(self):
        self.client.login(username="alice@example.org", password="password")

        form = {"set_password": "1"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 302

        # profile.token should be set now
        self.alice.profile.refresh_from_db()
        token = self.alice.profile.token

        #  Assert that the token is set
        self.assertNotEquals(token, None)

        # Assert that the email was sent and check email content
        self.assert_mail_sent_and_content('Set password on healthchecks.io',
                                          "Here's a link to set a password for your account on healthchecks.io:")

    def test_it_sends_report(self):
        check = Check(name="Test Check", user=self.alice)
        check.save()

        self.alice.profile.send_report()

        # Assert that the email was sent and check email content
        self.assert_mail_sent_and_content("Monthly Report", "This is a monthly report sent by healthchecks.io.")

    def test_it_adds_team_member(self):
        self.client.login(username="alice@example.org", password="password")

        form = {"invite_team_member": "1", "email": "frank@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        member_emails = set()
        for member in self.alice.profile.member_set.all():
            member_emails.add(member.user.email)

        # Assert the existence of the member emails
        # assertContains only works on HTTPResponse objects. Use assertIn for other objects
        self.assertIn("frank@example.org", member_emails)

        self.assertTrue("frank@example.org" in member_emails)

        # Assert that the email was sent and check email content
        self.assert_mail_sent_and_content("You have been invited to join " + self.alice.email + " on healthchecks.io",
                                          "" + self.alice.email + " invites you to their healthchecks.io account.")

    def test_add_team_member_checks_team_access_allowed_flag(self):
        self.client.login(username="charlie@example.org", password="password")

        form = {"invite_team_member": "1", "email": "frank@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 403

    def test_it_removes_team_member(self):
        self.client.login(username="alice@example.org", password="password")

        form = {"remove_team_member": "1", "email": "bob@example.org"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        self.assertEqual(Member.objects.count(), 0)

        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, None)

    def test_it_sets_team_name(self):
        self.client.login(username="alice@example.org", password="password")

        form = {"set_team_name": "1", "team_name": "Alpha Team"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 200

        self.alice.profile.refresh_from_db()
        self.assertEqual(self.alice.profile.team_name, "Alpha Team")

    def test_set_team_name_checks_team_access_allowed_flag(self):
        self.client.login(username="charlie@example.org", password="password")

        form = {"set_team_name": "1", "team_name": "Charlies Team"}
        r = self.client.post("/accounts/profile/", form)
        assert r.status_code == 403

    def test_it_switches_to_own_team(self):
        self.client.login(username="bob@example.org", password="password")

        self.client.get("/accounts/profile/")

        # After visiting the profile page, team should be switched back
        # to user's default team.
        self.bobs_profile.refresh_from_db()
        self.assertEqual(self.bobs_profile.current_team, self.bobs_profile)

    def test_it_shows_badges(self):
        self.client.login(username="alice@example.org", password="password")
        Check.objects.create(user=self.alice, tags="foo a-B_1  baz@")
        Check.objects.create(user=self.bob, tags="bobs-tag")

        r = self.client.get("/accounts/profile/")
        self.assertContains(r, "foo.svg")
        self.assertContains(r, "a-B_1.svg")

        # Expect badge URLs only for tags that match \w+
        self.assertNotContains(r, "baz@.svg")

        # Expect only Alice's tags
        self.assertNotContains(r, "bobs-tag.svg")

    # Test it creates and revokes API key
    def test_it_creates_and_revokes_api_key(self):
        self.client.login(username=self.alice.email, password="password")

        form = {"create_api_key": "1"}
        r = self.client.post("/accounts/profile/", form)

        # profile.api_key should be set now
        self.alice.profile.refresh_from_db()
        api_key = self.alice.profile.api_key

        # Assert that the api key is set
        self.assertNotEquals(api_key, None)

        form = {"revoke_api_key": "1"}
        r = self.client.post("/accounts/profile/", form)

        # profile.api_key should be set none
        self.alice.profile.refresh_from_db()
        api_key = self.alice.profile.api_key
        # Assert the api key is none
        self.assertEqual(api_key, "")
