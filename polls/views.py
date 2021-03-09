import datetime as dt

from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    RetrieveModelMixin, ListModelMixin, CreateModelMixin
)
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from polls.models import Poll, Submission
from polls.serializers import (
    PollSerializer, QuestionSerializer, SubmissionSerializer
)


class AdminPollViewSet(ModelViewSet):
    queryset = Poll.objects.prefetch_related(
        'questions', 'questions__options').all()
    serializer_class = PollSerializer
    permission_classes = [IsAuthenticated]


class AdminQuestionViewSet(ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        poll = get_object_or_404(
            Poll.objects.prefetch_related('questions', 'questions__options'),
            id=self.kwargs['poll_id']
        )

        return poll.questions.all()

    def perform_create(self, serializer):
        poll = self._get_poll_or_404(self.kwargs)
        serializer.save(poll=poll)

    def _get_poll_or_404(self, kwargs):
        try:
            return Poll.objects.get(id=kwargs['poll_id'])
        except Poll.DoesNotExist:
            raise NotFound('Poll not found.')


class ActivePollsViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    serializer_class = PollSerializer

    def get_queryset(self):
        now = dt.datetime.now()
        return Poll.objects.prefetch_related(
            'questions', 'questions__options'
        ).filter(
            start_date__lt=now, end_date__gt=now
        )


class SubmitViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = SubmissionSerializer

    def perform_create(self, serializer):
        poll = self._get_poll_or_404(self.kwargs)
        serializer.save(poll=poll)

    def _get_poll_or_404(self, kwargs):
        try:
            now = dt.datetime.now()
            return Poll.objects.prefetch_related(
                'questions', 'questions__options'
            ).filter(
                start_date__lt=now, end_date__gt=now
            ).get(
                pk=kwargs['poll_id']
            )
        except Poll.DoesNotExist:
            raise NotFound('Poll not found.')


class UserSubmissionsViewSet(ListModelMixin, GenericViewSet):
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.prefetch_related(
            'answers', 'answers__selected_options'
        ).filter(
            user_id=self.kwargs['user_id']
        )
