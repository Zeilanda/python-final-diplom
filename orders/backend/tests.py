from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
class CustomerTestCase(APITestCase):

    # register_url = '/api/registration/customer'
    register_url = reverse('backend:register-customer')
    verify_email_url = reverse('backend:user-register-confirm')
    login_url = reverse('backend:user_login')


    def test_register(self):

        # register data
        data = {
            "email": "user34@example-email.com",
            "password1": "verysecret1234",
            "password2": "verysecret1234",
            "first_name": "first_name",
            "last_name": "last_name",
            "city": "BigApple",
            "street": "apple_street",
            "house": "5",
            "phone": "5678907"
        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["detail"], "Verification e-mail sent.")

