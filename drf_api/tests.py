from django.core.mail import send_mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch
import os

class ContactUsViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('contact_us')
        self.valid_payload = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'message': 'This is a test message.'
        }
        self.invalid_payload = {
            'name': '',
            'email': '',
            'message': ''
        }

    @patch('drf_api.views.send_mail')
    def test_contact_us_view_success(self, mock_send_mail):
        """
        Test successful contact form submission and email sending.
        """
        mock_send_mail.return_value = 1  # Mock a successful email send
        response = self.client.post(self.url, self.valid_payload, format='json')

        # Ensure send_mail was called with the right parameters
        mock_send_mail.assert_called_once_with(
            'New Contact Form Submission from John Doe',
            'Message from John Doe (john.doe@example.com):\n\nThis is a test message.',
            'john.doe@example.com',
            [os.environ.get('EMAIL_HOST_USER')],
            fail_silently=False,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Message sent successfully.')

    def test_contact_us_view_invalid_payload(self):
        """
        Test invalid payload where required fields are missing.
        """
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
