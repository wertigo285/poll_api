from django.conf import settings
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from .views import (
     AdminPollViewSet, AdminQuestionViewSet, ActivePollsViewSet,
     SubmitViewSet, UserSubmissionsViewSet
)
router = SimpleRouter()

router.register(r'admin/polls',
                AdminPollViewSet,
                basename='polls')
router.register(r'admin/polls/(?P<poll_id>[^/d]+)/questions',
                AdminQuestionViewSet,
                basename='questions')
router.register(r'polls',
                ActivePollsViewSet,
                basename='polls')
router.register(r'polls/(?P<poll_id>[^/d]+)/submissions',
                SubmitViewSet,
                basename='submissions')
router.register(r'users/(?P<user_id>[^/d]+)/submissions',
                UserSubmissionsViewSet,
                basename='submissions')


urlpatterns = [
     path('', include(router.urls))
]
