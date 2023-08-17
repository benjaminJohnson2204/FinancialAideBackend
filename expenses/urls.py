from django.urls import path

from expenses.views import *

urlpatterns = [
    path('expenses', ExpenseListCreateView.as_view(), name='expense_list'),
    path('expenses/<int:pk>', ExpenseDetailView.as_view(), name='expense_detail'),
    path('expenses/by_category', ExpensesByCategoryView.as_view(), name='expenses_by_category'),
    path('expenses/csv_export', ExpensesCSVExportView.as_view(), name='expenses_csv_export')
]
