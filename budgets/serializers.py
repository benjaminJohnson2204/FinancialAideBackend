from rest_framework import serializers

from budgets.models import *

from users.serializers import UserResponseSerializer


class BudgetCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = [
            'name',
            'description',
            'start_time',
            'end_time',
            'interval',
            'income',
            'user',
        ]


class BudgetResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = [
            'name',
            'description',
            'start_time',
            'end_time',
            'interval',
            'income',
            'user',
            'created_at',
            'updated_at',
            'id',
        ]

    user = UserResponseSerializer()


class BudgetCategoryResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategory
        fields = [
            'name',
            'typical_percentage',
            'typical_monthly_amount',
            'id',
        ]


class BudgetCategoryRelationCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategoryRelation
        fields = [
            'budget',
            'category',
            'amount',
            'is_percentage'
        ]


class BudgetCategoryRelationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategoryRelation
        fields = [
            'budget',
            'category',
            'amount',
            'is_percentage',
            'id',
        ]

    budget = BudgetResponseSerializer()
    category = BudgetCategoryResponseSerializer()


class BudgetCategoryRelationBulkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetCategoryRelation
        fields = [
            'category',
            'amount',
            'is_percentage',
            'id',
        ]

    # Need to manually set this, by default ID is readonly
    id = serializers.IntegerField(required=False)


class BudgetCategoryRelationsBulkUpdateSerializer(serializers.Serializer):
    class Meta:
        fields = [
            'category_relations',
        ]

    category_relations = BudgetCategoryRelationBulkUpdateSerializer(many=True)
