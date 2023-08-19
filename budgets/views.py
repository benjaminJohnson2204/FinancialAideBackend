import csv

from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, views
from rest_framework.filters import SearchFilter

from budgets.models import *
from budgets.permissions import *
from budgets.serializers import *
from expenses.models import Expense
from utils.serializers import EmptySerializer


@extend_schema(
    tags=['Budgets'],
    description='List/create budgets',
    responses=BudgetResponseSerializer
)
class BudgetListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Budget.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BudgetResponseSerializer
        return BudgetCreationSerializer

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data={
            **request.data,
            'user': request.user.pk,
        })
        request_serializer.is_valid(raise_exception=True)
        self.perform_create(request_serializer)
        response_serializer = BudgetResponseSerializer(request_serializer.instance)
        headers = self.get_success_headers(response_serializer.data)
        return views.Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    tags=['Budgets'],
    description='Retrieve, update, or delete a budget',
    responses=BudgetResponseSerializer
)
class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsMyBudget)
    queryset = Budget.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BudgetResponseSerializer
        return BudgetCreationSerializer


@extend_schema(
    tags=['Budget Categories'],
    description='Get a list of all budget categories'
)
class BudgetCategoryListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BudgetCategoryResponseSerializer
    queryset = BudgetCategory.objects.all()
    filter_backends = (SearchFilter,)
    search_fields = ['name']


@extend_schema(
    tags=['Budget Category Relations'],
    description='List/create budget category relations',
    responses=BudgetCategoryRelationResponseSerializer
)
class BudgetCategoryRelationListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsMyBudgetCategoryRelationCreation,)
    queryset = BudgetCategoryRelation.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['budget', 'category']

    def get_queryset(self):
        return self.queryset.filter(budget__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BudgetCategoryRelationResponseSerializer
        return BudgetCategoryRelationCreationSerializer

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        self.perform_create(request_serializer)
        response_serializer = BudgetCategoryRelationResponseSerializer(request_serializer.instance)
        headers = self.get_success_headers(response_serializer.data)
        return views.Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    tags=['Budget Category Relations'],
    description='Retrieve, update, or delete a budget category relation',
    responses=BudgetCategoryRelationResponseSerializer
)
class BudgetCategoryRelationDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsMyBudgetCategoryRelationDetail)
    queryset = BudgetCategoryRelation.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return BudgetCategoryRelationResponseSerializer
        return BudgetCategoryRelationCreationSerializer


@extend_schema(
    tags=['Budget Category Relations'],
    description='Bulk update the category relations for this budget'
)
class BudgetCategoryRelationBulkUpdateView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, IsMyBudget)
    queryset = Budget.objects.all()
    serializer_class = BudgetCategoryRelationsBulkUpdateSerializer

    def patch(self, request, *args, **kwargs):
        budget = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_update = []
        to_create = []
        existing_ids = []
        for category_relation_data in serializer.data['category_relations']:
            category_relation = BudgetCategoryRelation(
                category=BudgetCategory.objects.get(pk=category_relation_data['category']),
                amount=category_relation_data['amount'],
                is_percentage=category_relation_data['is_percentage'],
                budget=budget,
            )
            if 'id' in category_relation_data:
                category_relation.id = category_relation_data['id']
                to_update.append(category_relation)
                existing_ids.append(category_relation.id)
            else:
                to_create.append(category_relation)

        # Delete any category relations that are not in request
        budget.categories.exclude(id__in=existing_ids).delete()

        BudgetCategoryRelation.objects.bulk_create(to_create)
        BudgetCategoryRelation.objects.bulk_update(to_update, ['category', 'amount', 'is_percentage'])
        return views.Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Budgets'],
    description='Get a CSV file of planned and actual spending by category for this budget'
)
class PlannedActualSpendingExportView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated, IsMyBudget)
    serializer_class = EmptySerializer
    queryset = Budget.objects.all()

    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={
                'Content-Disposition': 'attachment;filename="spending_comparison.csv"'
            }
        )
        budget = self.get_object()
        expenses = Expense.objects.filter(user=request.user)
        actual_spending_by_category = BudgetCategory.objects.get_actual_spending_by_category(expenses)
        categories_to_actual_spending = {
            spending['id']: spending['total_amount'] for spending in actual_spending_by_category
        }
        writer = csv.writer(response)
        writer.writerow(['Category', 'Planned ($)', 'Actual ($)'])
        for category_relation in budget.categories.all():
            amount = category_relation.get_total_amount()
            writer.writerow([
                category_relation.category.name,
                amount,
                categories_to_actual_spending[category_relation.category.id]
            ])

        return response
