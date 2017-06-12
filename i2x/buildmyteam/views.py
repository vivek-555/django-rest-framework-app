# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from i2x.buildmyteam.serializers import (
    UserSerializer,
    GroupSerializer,
    TeamSerializer,
    UserVerificationSerialzer,
    # TeamMembersSerializer
)
from .models import Team, UserVerification
from rest_framework.decorators import api_view, detail_route, list_route, permission_classes
from django.core.mail import send_mail
from permissions import IsOwnerOrReadOnly
from ..utility import *


# Create your views here.
class UserViewset(viewsets.ModelViewSet):
    """
    Endpoint allows users to be created/retrieved/updated/destroyed
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewset(viewsets.ModelViewSet):
    """ 
    Endpoint allows groups to be created/retrieved/updated/destroyed
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TeamViewset(viewsets.ModelViewSet):
    """
    Endpoint allows teams to be created/retrieved/updated/destroyed
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    @list_route()
    def test(self, request):
        """
        Testing framework
        :param request: 
        :return: 
        """

        teams = Team.objects.all()
        serializer = self.get_serializer(teams, many=True)

        subject = "Test email"
        message = "This is a test message"
        from_email = "vivek.d.techi@gmail.com"
        recipient = "vivekrajan555@gmail.com"

        send_mail(subject, message, from_email, [recipient], fail_silently=False)

        return Response(serializer.data)

    @detail_route(methods=['get', 'post'], serializer_class=TeamSerializer)
    def add_member(self, request, pk=None):
        """
        This adds your team
        :param request: default
        :param pk: primary key of Team
        :return: returns the team corresponds to Primary Key for GET
                 returns the team after adding team member for POST
        """
        # team = self.get_object()

        # serializer = TeamSerializer

        if request.method == "GET":

            queryset = Team.objects.all().get(id=pk)
            serializer = self.get_serializer(queryset)
            # serializer = TeamSerializer(queryset, context={'request': request})
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(data=request.data, context={'request':request})
            if serializer.is_valid():
                # team.set_password(serializer.data['password'])
                serializer.save()
                return Response({'status': 'member added'})
            else:
                return Response(serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

    # def get_serializer(self, *args, **kwargs):
    #
    #     """
    #     Return the serializer instance that should be used for validating and
    #     deserializing input, and for serializing output.
    #     """
    #
    #     serializer_class = TeamSerializer
    #     # kwargs['context'] = self.get_serializer_context()
    #     return serializer_class(*args, **kwargs)


class AddTeamMemberView(APIView):
    metadata_class = Team
    permission_classes = [IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            return Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            raise status.Http404

    def put(self, request, pk, format=None):

        team = self.get_object(pk)

        serializer_context = {
            'request': request,
            'name': team.name
        }

        request_data = request.data

        if request_data.get("name") is None:
            request_data["name"] = team.name

        serializer = TeamSerializer(team, data=request.data, context=serializer_context)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(http_method_names=['POST'])
def register(request):
    username = request.data["username"]
    email = request.data["email"]
    password = request.data["password"]
    verification_code = get_random_code()

    data = dict(username=username, email=email, password=password)

    serializer_context = {
        'request': request,
        'code': verification_code
    }

    serializer = UserSerializer(data=data, context=serializer_context)
    if serializer.is_valid():
        serializer.save()
        api_url = 'http://' + request.get_host() + "/confirm_email"
        send_registration_mail(username, email, verification_code, api_url)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(http_method_names=['POST'])
def confirm_email(request):
    email = request.data["email"]
    code = request.data["code"]

    user = User.objects.filter(email=email.strip().lower()).first()

    # if user exists and code match is confirmed then go ahead
    if user and user.verification.code == code.strip().upper():
        user.verification.code = ''
        user.verification.save()

        return Response({'confirmed': 'true'}, status=status.HTTP_200_OK)

    return Response({'message': "Verification code doesn't match"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(http_method_names=['POST'])
def reset(request):
    """
    Triggers the forgot password email having link to reset password
    :param: email
    :return: HTTP status codes - 200 for success and 422 for failure
    """
    email = request.data['email']

    if is_string_blank(email):   # return if no email is provided with 422 code
        return Response({'message': "No email provided"},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    email = email.strip().lower()
    verification_code = get_random_code()

    user = User.objects.filter(email=email).first()

    if user:
        api_url = 'http://' + request.get_host() + "/password"

        user.verification.code = verification_code
        user.verification.save()

        send_forgot_password_mail(user.first_name, email, verification_code, api_url)

        return Response(status=status.HTTP_200_OK)

    return Response({'message': "User with email:" + email + " don't exist in our system "},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)


@api_view(http_method_names=['POST'])
@permission_classes((IsOwnerOrReadOnly, ))
def change_password(request):
    """
    User can set the password from here using verification CODE provided in the email
    :return: HTTP status codes - 200 for success and 422 for failure
    """
    email = request.data["email"]
    new_password = request.data["password"]
    code = request.data["code"]

    if is_string_blank(email) or is_string_blank(new_password) or is_string_blank(code):
        return Response({'message': 'All email, password and code is needed'},
                        status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    email = email.strip().lower()
    user = User.objects.filter(email=email).first()

    if user and user.verification.code == code.strip().upper():
        user.set_password(new_password)
        user.save()

        user.verification.code = ''
        user.verification.save()

        password_changed_mail(user.first_name, email)  # update user about password change
        return Response(status=status.HTTP_200_OK)

    return Response({"message": "Either email or code doesn't match"},
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY)
