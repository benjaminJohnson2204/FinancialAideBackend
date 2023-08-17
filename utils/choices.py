"""
Choices (enums) that are used across multiple apps
"""

from django.db import models
from django.utils.translation import gettext_lazy


class TimeInterval(models.TextChoices):
    YEARLY = 'yearly', gettext_lazy('Yearly')
    MONTHLY = 'monthly', gettext_lazy('Monthly')
    WEEKLY = 'weekly', gettext_lazy('Weekly')
