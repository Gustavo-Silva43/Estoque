from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True,
        auto_now=False
        )
    modified = models.DateTimeField(
        'modificado em',
        auto_now=True,
        auto_now_add=False
        )
    
    class Meta:
        abstract = True