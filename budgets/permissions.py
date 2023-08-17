from rest_framework import permissions

from budgets.models import Budget


class IsMyBudget(permissions.BasePermission):
    """
    Grants permission to a user to access a budget only if
    they own it
    """
    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.user.pk


class IsMyBudgetCategoryRelationCreation(permissions.BasePermission):
    """
    Grants permission to a user to create a budget category relation
    only if they own the budget that it relates to
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True # Read-only is always OK
        budget = Budget.objects.get(pk=request.data.get('budget'))
        return budget.user.pk == request.user.pk


class IsMyBudgetCategoryRelationDetail(permissions.BasePermission):
    """
    Grants permission to a user to access a budget category relation
    only if they own the budget that it relates to
    """
    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.budget.user.pk
