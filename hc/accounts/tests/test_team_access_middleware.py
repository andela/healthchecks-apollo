from django.contrib.auth.models import User
from django.test import TestCase
from hc.accounts.models import Profile


class TeamAccessMiddlewareTestCase(TestCase):

    def test_it_handles_missing_profile(self):
        user = User(username="ned", email="ned@example.org")
        user.set_password("password")
        user.save()

        self.client.login(username="ned@example.org", password="password")
        r = self.client.get("/about/")
        self.assertEqual(r.status_code, 200)

        # Assert the new Profile objects count
        user_profile = Profile.objects.count()
        self.assertEqual(user_profile, 1)

        user_profile = Profile.objects.get(user=user)
        self.assertEqual(user_profile.user.email, "ned@example.org")
