from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate

from backend.models import User
from backend.views import AccountCustomerDetails


class CustomerTestCase(APITestCase):

    # register_url = '/api/registration/customer'
    register_url = reverse('backend:register-customer')
    verify_email_url = reverse('backend:user-register-confirm')
    login_url = reverse('backend:user_login')
    customer_details = reverse('backend:user-details')


    def test_register_customer(self):

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

        # try to login - should fail, because email is not verified
        login_data = {
            "email": data["email"],
            "password": data["password1"],
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "A user with this email and password was not found." in response.json()["non_field_errors"]
        )

        # force authenticate
        factory = APIRequestFactory()
        user = User.objects.get(email='user34@example-email.com')
        # users = User.objects.values()
        #
        # print(users)
        view = AccountCustomerDetails.as_view()
        # Make an authenticated request to the view...
        request = factory.get(self.customer_details)
        force_authenticate(request, user=user)
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)



class ProviderTestCase(APITestCase):

    register_url = reverse('backend:register-provider')
    verify_email_url = reverse('backend:user-register-confirm')
    login_url = reverse('backend:user_login')

    def test_register_provider(self):

        # register data
        data = {
            "email": "xy-manager@example-email.com",
            "password1": "verysecret1234",
            "password2": "verysecret1234",
            "first_name": "first_name",
            "last_name": "last_name",
            "shop": "XY-store",
            "position": "manager",

        }

        response = self.client.post(self.register_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["detail"], "Verification e-mail sent.")

        # try to login - should fail, because email is not verified
        login_data = {
            "email": data["email"],
            "password": data["password1"],
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(
            "A user with this email and password was not found." in response.json()["non_field_errors"]
        )