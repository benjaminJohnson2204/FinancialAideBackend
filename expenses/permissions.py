from rest_framework import permissions

from expenses.models import Expense


class IsMyExpense(permissions.BasePermission):
    """
    Grants permission to a user to access an expense only if
    they own it
    """
    def has_object_permission(self, request, view, obj):
        return request.user.pk == obj.user.pk
