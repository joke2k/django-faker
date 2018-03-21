from django.db import models


# 'Realistic' Example Models

class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_date = models.DateField()
    updated_time = models.TimeField()
    active = models.BooleanField()
    max_score = models.BigIntegerField()


class Player(models.Model):
    nickname = models.CharField(max_length=100)
    score = models.BigIntegerField()
    last_login_at = models.DateTimeField()

    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Action(models.Model):
    ACTION_FIRE = 'fire'
    ACTION_MOVE = 'move'
    ACTION_STOP = 'stop'

    ACTIONS = (
        (ACTION_FIRE, 'Fire'),
        (ACTION_MOVE, 'Move'),
        (ACTION_STOP, 'Stop'),
    )

    name = models.CharField(max_length=4, choices=ACTIONS)
    executed_at = models.DateTimeField()

    actor = models.ForeignKey(Player, related_name='actions', null=True, on_delete=models.CASCADE)
    target = models.ForeignKey(Player, related_name='enemy_actions+', null=True, on_delete=models.CASCADE)


class Assessment(models.Model):
    slug = models.SlugField(max_length=2, unique=True)


class Question(models.Model):
    title = models.TextField(max_length=255)
    order = models.SmallIntegerField()
    important = models.BooleanField()


class AnswerSubmission(models.Model):
    file = models.BinaryField(max_length=2000)
    first_name = models.TextField(max_length=255)
    last_name = models.TextField(max_length=255)


class Company(models.Model):
    name = models.TextField(max_length=255)
    address = models.TextField(max_length=4000)
    city = models.TextField(max_length=255)
    state = models.TextField(max_length=255)


class Answer(models.Model):
    assessment = models.ForeignKey(Assessment, related_name="answers", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    submission = models.OneToOneField(AnswerSubmission, related_name="answer", on_delete=models.CASCADE)
    company = models.ManyToManyField(Company, related_name="answers")

    class Meta:
        unique_together = (("assessment", "question"),)

# Relational Models


class ToOne(models.Model):
    thing = models.TextField()


class One(models.Model):
    to_one = models.OneToOneField(ToOne, related_name="one", on_delete=models.CASCADE)


class ToMany(models.Model):
    thing = models.TextField()


class Many(models.Model):
    to_many = models.ManyToManyField(ToMany, related_name="one")


class Key(models.Model):
    thing = models.TextField()


class Foreign(models.Model):
    key = models.ForeignKey(Key, related_name="foreigns", null=False, on_delete=models.CASCADE)
    key_null = models.ForeignKey(ToOne, related_name="foreigns", null=True, on_delete=models.CASCADE)


# Named fields

class NamedFields(models.Model):
    is_boolean = models.TextField()
    created_at = models.TextField()
    first_name = models.TextField()
    last_name = models.TextField()
    name = models.TextField()
    login = models.TextField()
    email = models.TextField()
    phone_number = models.TextField()
    address = models.TextField()
    city = models.TextField()
    street_address = models.TextField()
    zipcode = models.TextField()
    state = models.TextField()
    country = models.TextField()
    title = models.TextField()
    description = models.TextField()
