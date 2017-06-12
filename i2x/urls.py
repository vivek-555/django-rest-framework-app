"""i2x URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from i2x.buildmyteam import views
from rest_framework.documentation import include_docs_urls
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import login, logout
from rest_framework_swagger.views import get_swagger_view

router = routers.DefaultRouter()
router.register(r'users', views.UserViewset)
router.register(r'groups', views.GroupViewset)
router.register(r'teams', views.TeamViewset)

schema_view = get_swagger_view(title='Pastebin API')

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # url(r'^$', schema_view),
    url(r'^admin/', admin.site.urls),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', schema_view),
    # url(r'^docs/', include_docs_urls(title='BuildMyTeam API')),
    # url(r'^docs/', include('rest_framework_docs.urls')),
    url(r'^register/', views.register),
    url(r'^confirm_email/', views.confirm_email),
    url(r'^reset/', views.reset),
    url(r'^password/', views.change_password),
    url(r'^login/', login),
    url(r'^logout/', logout),


    url(r'^add-member/(?P<pk>[0-9]+)/$', views.AddTeamMemberView.as_view()),
    # url(r'^teams/{pk}/add-member/$', views.TeamViewset.add_member),

    # url(r'^test/$', views.TeamViewset.get_test.as_view())
]
urlpatterns += staticfiles_urlpatterns()

# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # in case of media
