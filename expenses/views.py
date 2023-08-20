import csv

from django.db.models import Sum, F, FloatField, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions, status, views
from rest_framework.filters import SearchFilter, OrderingFilter

from expenses.filters import ExpensesFilter
from expenses.models import *
from expenses.permissions import *
from expenses.serializers import *
from utils.serializers import EmptySerializer


@extend_schema(
    tags=['Expenses'],
    description='List/create expenses',
    responses=ExpenseResponseSerializer
)
class ExpenseListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Expense.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ExpensesFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'timestamp', 'description', 'category', 'amount']

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ExpenseResponseSerializer
        return ExpenseCreationSerializer

    def create(self, request, *args, **kwargs):
        request_serializer = self.get_serializer(data={
            **request.data,
            'user': request.user.pk,
        })
        request_serializer.is_valid(raise_exception=True)
        self.perform_create(request_serializer)
        response_serializer = ExpenseResponseSerializer(request_serializer.instance)
        headers = self.get_success_headers(response_serializer.data)
        return views.Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@extend_schema(
    tags=['Expenses'],
    description='Retrieve/update/delete expenses',
    responses=ExpenseResponseSerializer
)
class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated, IsMyExpense)
    queryset = Expense.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ExpenseResponseSerializer
        return ExpenseCreationSerializer


@extend_schema(
    tags=['Expenses'],
    description='Get total actual spending for each budget category'
)
class ExpensesByCategoryView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ExpensesByCategorySerializer
    queryset = Expense.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ExpensesFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'timestamp', 'description', 'category', 'amount']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        categories_queryset = BudgetCategory.objects.get_actual_spending_by_category(queryset)
        paginated_queryset = self.paginate_queryset(categories_queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


@extend_schema(
    tags=['Expenses'],
    description='Get a CSV file with the user\'s expenses (can be filtered)'
)
class ExpensesCSVExportView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = EmptySerializer
    queryset = Expense.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_class = ExpensesFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'timestamp', 'description', 'category', 'amount']

    def get_queryset(self):
        return Expense.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        response = HttpResponse(
            content_type="text/csv",
            headers={
                'Content-Disposition': 'attachment;filename="expenses.csv"'
            }
        )
        writer = csv.writer(response)
        writer.writerow(['Name', 'Date', 'Time', 'Description', 'Category', 'Amount', 'ID'])
        for expense in self.get_queryset():
            writer.writerow([
                expense.name or '-',
                expense.timestamp.strftime('%m/%d/%Y'),
                expense.timestamp.strftime('%I:%M %p'),
                expense.description or '-',
                '-' if expense.category is None else expense.category.name,
                expense.amount,
                expense.pk
            ])

        return response



