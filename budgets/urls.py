from django.urls import path

from budgets.views import *

urlpatterns = [
    path('budgets', BudgetListCreateView.as_view(), name='budget_list'),
    path('budgets/<int:pk>', BudgetDetailView.as_view(), name='budget_detail'),
    path('budgets/<int:pk>/category_relations/bulk_update', BudgetCategoryRelationBulkUpdateView.as_view(), name='budget_category_relation_bulk_update'),
    path('budgets/<int:pk>/spending_export', PlannedActualSpendingExportView.as_view(), name='planned_actual_spending'),
    path('budget_categories', BudgetCategoryListView.as_view(), name='budget_category_list'),
    path('budget_category_relations', BudgetCategoryRelationListCreateView.as_view(), name='budget_category_relation_list'),
    path('budget_category_relations/<int:pk>', BudgetCategoryRelationDetailView.as_view(), name='budget_category_relation_detail'),
]
