from django_filters import rest_framework as filters

from expenses.models import Expense


class ExpensesFilter(filters.FilterSet):
    class Meta:
        model = Expense
        fields = {
            'category': ['exact', 'in'],
            'timestamp': ['exact', 'lte', 'gte']
        }
