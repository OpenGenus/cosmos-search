from django.db import models

VOTES_CHOICES = [
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
]


class Votes(models.Model):
    project_name = models.CharField(max_length=500, null=True, blank=True)
    vote_value = models.CharField(choices=VOTES_CHOICES, default='1', max_length=20, null=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.vote_value
