from django.db import transaction
from rest_framework import serializers

from polls.models import (
    Poll, Question, Option,
    Submission, Answer, SelectedOption,
    QUESTION_TYPES, QUESTION_TYPES_DICT
)


TEXT = QUESTION_TYPES_DICT['TEXT']
CHOICE = QUESTION_TYPES_DICT['CHOICE']
MULTIPLY_CHOICE = QUESTION_TYPES_DICT['MULTIPLY_CHOICE']
OPTIONS_REQUIRED = [CHOICE, MULTIPLY_CHOICE]


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ['id', 'description']


class QuestionSerializer(serializers.ModelSerializer):
    question_type = serializers.ChoiceField(choices=QUESTION_TYPES, label='Тип вопроса')
    options = OptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'options']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if instance.question_type not in OPTIONS_REQUIRED:
            data.pop('options')
        return data

    def validate(self, attrs):
        if attrs['question_type'] == TEXT and 'options' in attrs:
            raise serializers.ValidationError(
                f'"options" should be empty with question_type "{TEXT}"')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        options = self._get_options(validated_data)
        question = Question.objects.create(**validated_data)
        self._create_options(question, options)
        return question

    @transaction.atomic
    def update(self, instance, validated_data):
        q_type = validated_data['question_type']
        if q_type == TEXT or 'options' in validated_data:
            instance.options.all().delete()
            options = self._get_options(validated_data)
            self._create_questions(instance, options)

        return super().update(instance, validated_data)

    def _create_options(self, question, options):
        for option_data in options:
            option = OptionSerializer(
                data={'question': question, **option_data})
            option.is_valid(raise_exception=True)
            option.save(question=question)

    def _get_options(self, data):
        return data.pop('options') if 'options' in data else []


class PollSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'start_date',
                  'end_date', 'description', 'questions']

    def validate_start_date(self, value):
        if self.instance and self.instance.start_date != value:
            raise serializers.ValidationError(
                'start_date is immutable once set')
        return value

    def validate(self, attrs):
        if 'start_date' in attrs and attrs['start_date'] >= attrs['end_date']:
            raise serializers.ValidationError(
                'end_date must occur after start_date')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        questions = self._get_questions(validated_data)
        poll = Poll.objects.create(**validated_data)
        self._create_questions(poll, questions)
        return poll

    @transaction.atomic
    def update(self, instance, validated_data):
        if 'questions' in validated_data:
            instance.questions.all().delete()
            questions = validated_data.pop('questions')
            self._create_questions(instance, questions)
        return super().update(instance, validated_data)

    def _create_questions(self, poll, questions):
        for question_data in questions:
            question = QuestionSerializer(data={'poll': poll, **question_data})
            question.is_valid(raise_exception=True)
            question.save(poll=poll)

    def _get_questions(self, data):
        return data.pop('questions') if 'questions' in data else []


class SelectedOptionSerializer(serializers.ModelSerializer):
    answer = serializers.PrimaryKeyRelatedField(
        queryset=Answer.objects.all(), required=True, write_only=True)
    description = serializers.ReadOnlyField(source='option.description')

    class Meta:
        model = SelectedOption
        fields = ['answer', 'option', 'description']

    def validate(self, attrs):
        if self.context['question'] != attrs['option'].question:
            raise serializers.ValidationError(
                'option demands to other question')
        return attrs


class InputAnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), required=True)
    text = serializers.CharField(required=False)
    selected_options = serializers.ListField(
        child=serializers.IntegerField(min_value=0),
        required=False
    )


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.ReadOnlyField(source='question.text')
    question_type = serializers.ReadOnlyField(source='question.question_type')
    submission = serializers.PrimaryKeyRelatedField(
        queryset=Submission.objects.all(), required=True, write_only=True)

    class Meta:
        model = Answer
        fields = ['question', 'question_text',
                  'question_type', 'text', 'submission']


class TextAnswerSerializer(AnswerSerializer):
    text = serializers.CharField(required=True)


class OptionsAnswerMixin:

    class Meta:
        model = Answer
        exclude = ['text']

    def validate_selected_options(self, value):
        if not len(value):
            raise serializers.ValidationError(
                'Empty select_options not allowed')
        return value

    @transaction.atomic
    def create(self, validated_data):
        selected_options = validated_data.pop('selected_options')
        Answer.objects.filter(submission=validated_data['submission'],
                              question=validated_data['question']
                              ).delete()
        answer = Answer.objects.create(**validated_data)
        validated_data['selected_options'] = selected_options
        self._create_selected_options(answer=answer.pk, **validated_data)
        return answer

    def to_representation(self, instance):
        data = super().to_representation(instance)
        selected_options = self.instance.selected_options.all()
        serializer = SelectedOptionSerializer(selected_options, many=True)
        data['selected_options'] = serializer.data
        return data

    def _create_selected_options(self, **kwargs):
        answer, question = kwargs['answer'], kwargs['question']
        for option in kwargs['selected_options']:
            s_option = SelectedOptionSerializer(data={
                                                      'option': option,
                                                      'answer': answer
                                                      },
                                                context={'question': question})
            s_option.is_valid(raise_exception=True)
            s_option.save()


class ChoiceAnswerSerializer(OptionsAnswerMixin, AnswerSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(),
        many=True,
        required=True,
        write_only=True)

    def validate_selected_options(self, value):
        super().validate_selected_options(value)
        if len(value) != 1:
            raise serializers.ValidationError(
                'More than 1 selected option for choice question')
        return value


class MultiplyChoiceAnswerSerializer(OptionsAnswerMixin, AnswerSerializer):
    selected_options = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all(),
        many=True,
        required=True,
        write_only=True)


class SubmissionSerializer(serializers.ModelSerializer):
    answers = InputAnswerSerializer(many=True, required=True, write_only=True)
    poll_description = serializers.ReadOnlyField(source='poll.description')
    poll_title = serializers.ReadOnlyField(source='poll.title')

    class Meta:
        model = Submission
        fields = ['user_id', 'answers', 'poll_description',
                  'answers', 'poll_title']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['answers'] = []
        for answer in instance.answers.all():
            question_type = answer.question.question_type
            serializer = self._get_answer_serializer(question_type)
            data['answers'].append(serializer(answer).data)

        return data

    def validate_answers(self, value):
        errors = []
        poll = self.context['poll']
        poll_questions = set(q['id'] for q in poll.questions.values('id'))
        raw_sub_questions = [a['question'].id for a in value]
        sub_questions = set(raw_sub_questions)
        if len(sub_questions) < len(sub_questions):
            errors.append(
                'Duplicate questions in answers')
        not_answered = poll_questions.difference(sub_questions)
        for question_id in not_answered:
            errors.append(
                f'No answer for question {question_id}')
        unwanted = sub_questions.difference(poll_questions)
        for question_id in unwanted:
            errors.append(
                f'Unwanted answer for question {question_id}')
        if errors:
            raise serializers.ValidationError(errors)
        return value

    @transaction.atomic
    def create(self, validated_data):
        poll = self.context['poll']
        answers = validated_data.pop('answers')
        Submission.objects.filter(user_id=validated_data['user_id'],
                                  poll=poll
                                  ).delete()
        submission = Submission.objects.create(poll=poll, **validated_data)
        validated_data['answers'] = answers
        self._create_answers(submission=submission,
                             poll=poll,
                             **validated_data)
        return submission

    def _get_answer_serializer(self, q_type):
        if q_type == TEXT:
            return TextAnswerSerializer
        elif q_type == CHOICE:
            return ChoiceAnswerSerializer
        elif q_type == MULTIPLY_CHOICE:
            return MultiplyChoiceAnswerSerializer

    def _create_answers(self, **kwargs):
        poll, submission = kwargs['poll'], kwargs['submission']
        answers = kwargs['answers']

        for answer in answers:
            question = answer.pop('question')
            q_type = question.question_type
            serializer = self._get_answer_serializer(q_type)
            data = {'submission': submission.pk,
                    'question': question.id, **answer}
            answer = serializer(data=data, context={'poll': poll})
            answer.is_valid(raise_exception=True)
            answer.save()
