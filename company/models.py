from django.db import models


class TopEaners(models.Model) :
    name = models.CharField(max_length = 40)
    amount = models.PositiveIntegerField()

    