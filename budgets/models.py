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

    def get_duration_days(self):
        """
        Gets the duration of the budget, in days. Rounds down to the nearest day.
        """
        delta = self.end_time - self.start_time
        return delta.days

    def get_multiplier(self):
        """
        Returns the amount by which this budget's income should be
        multiplied to get the TOTAL income across the budget.
        For example, if a budget is monthly and lasts for 2.5 months,
        this function would return 2.5.
        """
        duration_days = self.get_duration_days()
        days_multiplier = 1
        if self.interval == TimeInterval.YEARLY:
            days_multiplier = 365
        elif self.interval == TimeInterval.MONTHLY:
            days_multiplier = 30
        elif self.interval == TimeInterval.WEEKLY:
            days_multiplier = 7
        return duration_days / days_multiplier


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

    def get_total_amount(self):
        """
        Gets the total amount (raw amount) allocated to this
        category relation across the entire budget
        """
        budget_multiplier = self.budget.get_multiplier()
        amount = self.amount
        if self.is_percentage:
            amount *= self.budget.income / 100
        return budget_multiplier * float(amount)


    class Meta:
        # Can't have more than 1 amount budgeted to same category for same budget
        unique_together = [["budget", "category"]]
        ordering = ['-budget__start_time', '-category__name'] # order by most recent budget, then alphabetical category
