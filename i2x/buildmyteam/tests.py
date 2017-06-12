# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse
from models import Team, UserVerification
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .views import *
import json

# Create your tests here.


class TeamModelTestCase(TestCase):
    """This class defines the test suite for Team model"""

    def setUp(self):
        """Define the test client and other test variables"""
        user = User.objects.create(username="vivek555@gmail.com")
        self.team_name = "Barcelona"
        self.team1 = Team(name=self.team_name, owner=user)

        self.team_name2 = "ManchesterUnited"
        self.members = [User.objects.create(username="mcb12345@gmail.com"),
                        User.objects.create(username="mcb54321@gmail.com")]
        self.team2 = Team(name=self.team_name2, owner=user)

    def test_model_can_create_a_team(self):
        """Test if Team model can create a team"""
        old_count = Team.objects.count()
        self.team1.save()
        new_count = Team.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_returns_readable_repr(self):
        """Test a readable representation returned from model"""
        self.assertEqual(str(self.team1), self.team_name)

    def test_model_add_team_members(self):
        """Test if team members can be added into team"""
        old_count = Team.objects.count()
        self.team2.save()
        new_count = Team.objects.count()
        self.assertNotEqual(old_count, new_count)

        self.team2.members = self.members
        self.team2.save()

        latest_team = Team.objects.get(id=self.team2.id)
        latest_team_members = [member for member in latest_team.members.all()]

        self.assertListEqual(latest_team_members, self.members)


class UserVerificationTestCase(TestCase):
    """This class defines the test suite for UserVerification model"""

    def setUp(self):
        """Define the test client and other test variables"""

        self.username = "vivek12345@gmail.com"
        user = User.objects.create(username=self.username)
        self.name = "Verification code for user:" + str(user.id)
        self.code = "TESTING100"

        self.user_verification = UserVerification(user=user, code=self.code)

    def test_model_can_create_a_verification_code(self):
        """Test if UserVerification model can save a verification code"""

        old_count = UserVerification.objects.count()
        self.user_verification.save()
        new_count = UserVerification.objects.count()
        self.assertNotEqual(old_count, new_count)

    def test_model_can_retrieve_a_verification_code(self):
        """Test if UserVerification model can retrieve same code for user"""

        self.user_verification.save()
        user = User.objects.get(username=self.username)

        self.assertEqual(user.verification.code, self.code)


class GeneralViewTestCase(TestCase):
    """Test suite for User api views"""

    def setUp(self):
        """Define the test client and other test variables"""

        self.email = "mcb00@gmail.com"
        self.password = "123456"
        self.user = User.objects.create(username=self.email, password=self.password, is_staff=True)
        UserVerification.objects.create(user=self.user, code='')

        # Initialize client and force it to use authentication
        self.user = User.objects.get(username=self.email)

        # #######  API authentication  #######

        #   ######### By pass authentication #############
        # self.client = APIClient()
        # self.client.force_authenticate(user=self.user)
        # self.client.login(username=self.email, password=self.password)

        #   ######### Token based authentication #############
        token = Token.objects.create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        # #######  End: API authentication  #######

        self.team_name = 'Asana'
        self.user_url = "http://127.0.0.1:8000/users/" + str(self.user.id) + "/"  # FIXME: better soln ?

        self.team = Team.objects.create(name=self.team_name, owner=self.user)
        self.add_member_data = {'owner': self.user_url,
                                'members_emails': 'mcb11@gmail.com, mcb22@gmail.com'
                                }
        self.team_request_url = "/add-member/" + str(self.team.id) + "/"
        self.add_member_response = self.client.put(self.team_request_url,
                                                   json.dumps(self.add_member_data),
                                                   content_type="application/json")

        self.register_data = {
            'username': 'mcb33@gmail.com',
            'email': 'mcb33@gmail.com',
            'password': '654321'
        }
        self.register_response = self.client.post("/register/",
                                                  json.dumps(self.register_data),
                                                  content_type="application/json")
        self.registered_user = User.objects.get(username=self.register_data["username"])

        self.confirm_email_data = {
            'email': self.registered_user.email,
            'code': self.registered_user.verification.code
        }
        self.confirm_email_response = self.client.post("/confirm_email/",
                                                       json.dumps(self.confirm_email_data),
                                                       content_type="application/json")
        self.confirmed_user = User.objects.get(email=self.confirm_email_data['email'])

        self.reset_password_data = {
            'email': self.confirmed_user.email
        }
        self.reset_password_response = self.client.post("/reset/",
                                                        json.dumps(self.reset_password_data),
                                                        content_type="application/json")
        self.reset_password_user = User.objects.get(email=self.reset_password_data['email'])

        self.new_password = "09876"
        self.change_password_data = {
            'email': self.reset_password_user.email,
            'password': self.new_password,
            'code': self.reset_password_user.verification.code
        }
        self.change_password_response = self.client.post("/password/",
                                                         json.dumps(self.change_password_data),
                                                         content_type="application/json")
        self.changed_password_user = User.objects.get(email=self.change_password_data['email'])

    def test_api_can_add_member_to_team(self):
        """Test if members can be added into the team"""

        add_member_response_code = self.add_member_response.status_code
        add_member_response = json.loads(self.add_member_response.content)

        self.assertEqual(add_member_response_code, status.HTTP_201_CREATED)
        self.assertItemsEqual(add_member_response["members_emails"],
                              self.add_member_data["members_emails"])

    def test_api_can_register_user(self):
        """Test if user can be registered"""
        register_response_code = self.register_response.status_code

        self.assertEqual(register_response_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(self.registered_user)
        self.assertNotEqual(self.registered_user.verification.code, "")

    def test_api_can_confirm_registered_email(self):
        """Test if user can confirm the registered email"""
        confirm_email_response_code = self.confirm_email_response.status_code

        self.assertEqual(confirm_email_response_code, status.HTTP_200_OK)
        self.assertEqual(self.confirmed_user.verification.code, "")

    def test_api_can_initiate_reset_password(self):
        """Test if user can initiate reset password - generates verification code"""

        reset_password_response_code = self.reset_password_response.status_code

        self.assertEqual(reset_password_response_code, status.HTTP_200_OK)
        self.assertNotEqual(self.reset_password_user.verification.code, "")

    def test_api_can_change_passwrd(self):
        """Test if user can change his password - verifies the code"""
        change_password_response_code = self.change_password_response.status_code

        self.assertEqual(change_password_response_code, status.HTTP_200_OK)
        self.assertEqual(self.changed_password_user.check_password(self.new_password), True)
