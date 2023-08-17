from rest_framework import serializers

from budgets.serializers import BudgetCategoryResponseSerializer
from expenses.models import *
from users.serializers import UserResponseSerializer


class ExpenseCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'name',
            'timestamp',
            'user',
            'description',
            'category',
            'amount',
        ]


class ExpenseResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = [
            'name',
            'timestamp',
            'user',
            'description',
            'category',
            'amount',
            'id',
        ]

    user = UserResponseSerializer()
    category = BudgetCategoryResponseSerializer()


class ExpensesByCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = [
            'total_amount',
            'id'
        ]

    total_amount = serializers.FloatField()