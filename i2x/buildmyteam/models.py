# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Team(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=False)
    description = models.CharField(max_length=250, blank=True)
    owner = models.ForeignKey('auth.User', related_name='owner')
    members = models.ManyToManyField('auth.User', related_name='members')

    def members_emails(self):
        return ", ".join([(lambda u: u.email)(u) for u in self.members.all()])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created',)


class UserVerification(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='verification')
    code = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return "Verification data for user:" + self.user.id

    # class Meta:
    #     db_table = 'buildmyteam_user_verification'


# class TeamMember(models.Model):
#     team_id = models.ForeignKey(Team, related_name='team_id')
#     user_id = models.ForeignKey('auth.User', related_name='user_id')
#
#     def __str__(self):
#         return str(self.team_id) + "->" + str(self.user_id)
