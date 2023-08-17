from django.contrib import admin

from budgets.models import *

admin.site.register(Budget)
admin.site.register(BudgetCategory)
admin.site.register(BudgetCategoryRelation)
