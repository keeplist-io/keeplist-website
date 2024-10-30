from django.test import TestCase
from django.urls import reverse

class ProfileViewTests(TestCase):
    def test_profile_view(self):
        response = self.client.get(reverse('profile', args=['nonexistentuser']))
        self.assertEqual(response.status_code, 404) 