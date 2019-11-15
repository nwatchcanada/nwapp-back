from django.db import models


class BigPkAbastract(models.Model):
    id = models.BigAutoField(primary_key=True)

    class Meta:
        abstract = True
