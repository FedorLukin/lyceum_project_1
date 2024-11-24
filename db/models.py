from django.db import models
from manage import init_django

init_django()


class regular_schedule(models.Model):
    lesson_number = models.IntegerField(blank=False)
    lesson_info = models.TextField(blank=False)
    class_letter = models.CharField(max_length=255, blank=False)
    group_number = models.IntegerField(blank=False)
    date = models.DateField(blank=False)


class uday_schedule(models.Model):
    lesson_number = models.IntegerField(blank=False)
    lesson_info = models.TextField(blank=False)
    group_number = models.IntegerField(blank=False)
    date = models.DateField(blank=False)


class users(models.Model):
    user_id = models.BigIntegerField(blank=False, primary_key=True)
    class_letter = models.CharField(blank=True, default=None)
    group_number = models.IntegerField(blank=True, default=0)
    u_group_number = models.IntegerField(blank=True, default=0)
