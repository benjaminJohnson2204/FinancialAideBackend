from django.contrib.auth import get_user_model
from django.db import models

from budgets.models import BudgetCategory


class Expense(models.Model):
    name = models.CharField(max_length=256, null=True)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    description = models.CharField(max_length=2048, null=True)
    category = models.ForeignKey(BudgetCategory, on_delete=models.SET_NULL, null=True, related_name='expenses')
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['-timestamp'] # show most recent first by default
