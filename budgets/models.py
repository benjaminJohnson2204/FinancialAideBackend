from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import FloatField, Subquery, OuterRef, Sum
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware

from utils.choices import TimeInterval


class Budget(models.Model):
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=2048, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    interval = models.CharField(max_length=16, choices=TimeInterval.choices)
    income = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='budgets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-end_time'] # show most recent first by default


class BudgetCategoriesManager(models.Manager):
    def get_actual_spending_by_category(self, expenses_queryset):
        return self.annotate(  # for each category
            total_amount=Coalesce(
                # find the total amount among expenses under that category
                Subquery(
                    # use existing queryset (may be filtered if desired)
                    expenses_queryset.filter(
                        category_id=OuterRef('id')
                        # by filtering by the category's ID
                    )
                    .values(
                        'category_id')  # necessary for GROUP BY category_id to work correctly
                    .annotate(total=Sum('amount'))
                    .values('total'),  # take the total
                    output_field=FloatField()
                ),
                0,  # Default to 0 if no expenses under category
                output_field=FloatField()
            )
        ).values('id', 'total_amount').order_by('-total_amount')


class BudgetCategory(models.Model):
    name = models.CharField(max_length=256)
    typical_percentage = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    typical_monthly_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True)

    objects = BudgetCategoriesManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name'] # show alphabetical order by default


class BudgetCategoryRelation(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='categories')
    category = models.ForeignKey(BudgetCategory, on_delete=models.CASCADE, related_name='relations')
    amount = models.DecimalField(max_digits=12, decimal_places=2, )
    is_percentage = models.BooleanField()

    class Meta:
        # Can't have more than 1 amount budgeted to same category for same budget
        unique_together = [["budget", "category"]]
        ordering = ['-budget__start_time', '-category__name'] # order by most recent budget, then alphabetical category
