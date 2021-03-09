from django.db import models
from django.core.validators import RegexValidator

# Типы вопросов
QUESTION_TYPES = ['text', 'choice', 'multiply_choice']
QUESTION_TYPES_DICT = {q_type.upper(): q_type for q_type in QUESTION_TYPES}


class Poll(models.Model):
    """
    Опрос
    """
    title = models.CharField('Название', max_length=150)
    start_date = models.DateTimeField('Начало',)
    end_date = models.DateTimeField('Окончание')
    description = models.TextField('Описание')
    last_change = models.DateTimeField('Дата прохождения', auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gt=models.F('start_date')),
                name="Period_check"
            )
        ]


class Question(models.Model):
    """
    Вопрос
    """
    poll = models.ForeignKey(Poll,
                             on_delete=models.CASCADE,
                             related_name='questions',
                             verbose_name='Опрос')
    text = models.TextField('Текст вопроса')
    question_type = models.CharField('Тип вопроса',
                                     max_length=100,
                                     validators=[
                                         RegexValidator(
                                             regex='|'.join(QUESTION_TYPES))
                                         ])


class Option(models.Model):
    """
    Вариант ответа
    """
    question = models.ForeignKey(Question,
                                 on_delete=models.CASCADE,
                                 related_name='options',
                                 verbose_name='Вопрос')
    description = models.CharField('Описание', max_length=100)


class Submission(models.Model):
    """
    Отправленный опрос
    """
    user_id = models.PositiveIntegerField('ID пользователя')
    poll = models.ForeignKey(Poll,
                             on_delete=models.CASCADE,
                             verbose_name='Опрос')
    poll_title = models.CharField('Название', max_length=150)
    poll_description = models.TextField('Описание')
    date = models.DateTimeField('Дата прохождения', auto_now=True)

    class Meta:
        unique_together = ['user_id', 'poll']


class Answer(models.Model):
    """
    Ответ
    """
    submission = models.ForeignKey(Submission,
                                   on_delete=models.CASCADE,
                                   verbose_name='Опрос пользователя',
                                   related_name='answers')
    question = models.ForeignKey(Question,
                                 on_delete=models.DO_NOTHING,
                                 verbose_name='Вопрос')
    question_text = models.TextField('Текст вопроса')
    question_type = models.CharField('Тип вопроса', max_length=100)
    text = models.TextField('Ответ')

    class Meta:
        unique_together = ['submission', 'question']


class SelectedOption(models.Model):
    """
    Выбранный вариант
    """
    answer = models.ForeignKey(Answer,
                               verbose_name='Ответ',
                               on_delete=models.CASCADE,
                               related_name='selected_options',)
    option = models.ForeignKey(Option,
                               verbose_name='Вариант',
                               on_delete=models.DO_NOTHING,
                               null=True)
    description = models.CharField('Описание', max_length=100)
