from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from budgets.models import Budget, BudgetCategory, BudgetCategoryRelation

from users.models import User
from utils.choices import TimeInterval


class BudgetTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create_user(
            username='user1',
            email='user1@gmail.com',
            password='password1',
        )
        cls.user2 = User.objects.create_user(
            username='user2',
            email='user2@gmail.com',
            password='password2',
        )
        cls.budget1 = Budget.objects.create(
            name='Budget 1',
            description='Test Budget 1',
            start_time=datetime.now(tz=timezone.utc),
            end_time=datetime.now(tz=timezone.utc),
            interval=TimeInterval.YEARLY,
            income=60000,
            user=cls.user1,
        )
        cls.budget2 = Budget.objects.create(
            name='Budget 2',
            start_time=datetime.now(tz=timezone.utc),
            end_time=datetime.now(tz=timezone.utc),
            interval=TimeInterval.MONTHLY,
            income=4500,
            user=cls.user2,
        )
        cls.budget_category1 = BudgetCategory.objects.create(
            name='category1',
            typical_percentage=15.50,
            typical_monthly_amount=400,
        )
        cls.budget_category2 = BudgetCategory.objects.create(
            name='category2',
            typical_percentage=26.75,
        )
        cls.budget_category3 = BudgetCategory.objects.create(
            name='category3',
            typical_monthly_amount=1000,
        )
        cls.budget_category_relation1 = BudgetCategoryRelation.objects.create(
            budget=cls.budget1,
            category=cls.budget_category1,
            amount=350,
            is_percentage=False
        )
        cls.budget_category_relation2 = BudgetCategoryRelation.objects.create(
            budget=cls.budget2,
            category=cls.budget_category2,
            amount=17.6,
            is_percentage=True
        )

    def test_create_budget_valid(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse('budget_list'),
            {
                'name': 'New Budget',
                'start_time': datetime.now(tz=timezone.utc),
                'end_time': datetime.now(tz=timezone.utc),
                'interval': TimeInterval.WEEKLY,
                'income': 1100,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['interval'], TimeInterval.WEEKLY)
        self.assertEqual(response.json()['user']['username'], 'user1')

    def test_create_budget_missing_fields(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse('budget_list'),
            {
                'name': 'New Budget',
                'start_time': datetime.now(tz=timezone.utc),
                'end_time': datetime.now(tz=timezone.utc),
                'interval': TimeInterval.WEEKLY,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_budget_unauthorized(self):
        response = self.client.post(
            reverse('budget_list'),
            {
                'name': 'New Budget',
                'start_time': datetime.now(tz=timezone.utc),
                'end_time': datetime.now(tz=timezone.utc),
                'interval': TimeInterval.WEEKLY,
                'income': 1100,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_budgets_valid(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('budget_list')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1) # Only 1 budget owned by user 1
        self.assertEqual(response.json()['results'][0]['id'], self.budget1.pk)

    def test_list_budgets_unauthorized(self):
        response = self.client.get(
            reverse('budget_list')
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cant_retrieve_other_users_budget(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('budget_detail', kwargs={
                'pk' : self.budget2.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_own_budget(self):
        self.client.login(username='user2', password='password2')
        response = self.client.get(
            reverse('budget_detail', kwargs={
                'pk' : self.budget2.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user']['id'], self.user2.pk)
        self.assertEqual(response.json()['interval'], self.budget2.interval)

    def test_cant_edit_other_users_budget(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('budget_detail', kwargs={
                'pk': self.budget2.pk
            }),
            {
                'income': 575,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure the budget didn't actually change
        self.assertEqual(Budget.objects.get(pk=self.budget2.pk).income, 4500)

    def test_edit_own_budget(self):
        self.client.login(username='user2', password='password2')
        response = self.client.patch(
            reverse('budget_detail', kwargs={
                'pk': self.budget2.pk
            }),
            {
                'income': 575,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the budget DID actually change
        self.assertEqual(Budget.objects.get(pk=self.budget2.pk).income, 575)

    def test_cant_delete_other_users_budget(self):
        self.client.login(username='user1', password='password1')
        response = self.client.delete(
            reverse('budget_detail', kwargs={
                'pk': self.budget2.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Ensure the budget didn't actually get deleted
        self.assertEqual(Budget.objects.filter(pk=self.budget2.pk).count(), 1)

    def test_delete_own_budget(self):
        self.client.login(username='user2', password='password2')
        response = self.client.delete(
            reverse('budget_detail', kwargs={
                'pk': self.budget2.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Ensure the budget DID actually get deleted
        self.assertEqual(Budget.objects.filter(pk=self.budget2.pk).count(), 0)

    def test_list_budget_categories(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('budget_category_list')
        )
        self.assertEqual(response.json()['count'], 3)

    def test_search_budget_categories(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('budget_category_list'),
            {
                'search': 'category1'
            }
        )
        self.assertEqual(response.json()['count'], 1)

    def test_create_budget_category_relation_duplicate(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse('budget_category_relation_list'),
            {
                'budget': self.budget1.pk,
                'category': self.budget_category1.pk,
                'amount': 375,
                'is_percentage': False,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_budget_category_relation_other_users_budget(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse('budget_category_relation_list'),
            {
                'budget': self.budget2.pk,
                'category': self.budget_category1.pk,
                'amount': 375,
                'is_percentage': False,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_budget_category_relation_ok(self):
        self.client.login(username='user2', password='password2')
        response = self.client.post(
            reverse('budget_category_relation_list'),
            {
                'budget': self.budget2.pk,
                'category': self.budget_category1.pk,
                'amount': 375,
                'is_percentage': False,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['budget']['user']['username'], 'user2')
        self.assertEqual(BudgetCategoryRelation.objects.filter(budget=self.budget2.pk, category=self.budget_category1.pk).count(), 1)

    def test_list_budget_category_relations(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('budget_category_relation_list')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)

    def test_filter_budget_category_relations(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('budget_category_relation_list'),
            {
                'budget': self.budget1.pk,
                'category': self.budget_category1.pk,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)
        response = self.client.get(
            reverse('budget_category_relation_list'),
            {
                'budget': self.budget1.pk,
                'category': self.budget_category2.pk,
            }
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

    def test_cant_bulk_update_other_users_budget_category_relations(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('budget_category_relation_bulk_update', kwargs={'pk': self.budget2.pk}),
            {
                'category_relations': []
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(BudgetCategoryRelation.objects.filter(budget=self.budget2).count(), 1)

    def test_bulk_update_remove_budget_category_relations(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('budget_category_relation_bulk_update', kwargs={'pk': self.budget1.pk}),
            {
                'category_relations': []
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BudgetCategoryRelation.objects.filter(budget=self.budget1).count(), 0)

    def test_bulk_update_add_budget_category_relation(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('budget_category_relation_bulk_update', kwargs={'pk': self.budget1.pk}),
            {
                'category_relations': [
                    {
                        'category': self.budget_category1.pk,
                        'amount': 350,
                        'is_percentage': False,
                        'id': self.budget_category_relation1.pk
                    },
                    {
                        'category': self.budget_category2.pk,
                        'amount': 500,
                        'is_percentage': False,
                    },
                    {
                        'category': self.budget_category3.pk,
                        'amount': 15.5,
                        'is_percentage': True,
                    },
                ]
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BudgetCategoryRelation.objects.filter(budget=self.budget1).count(), 3)

    def test_bulk_update_change_category_relation(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('budget_category_relation_bulk_update', kwargs={'pk': self.budget1.pk}),
            {
                'category_relations': [
                    {
                        'category': self.budget_category1.pk,
                        'amount': 6.8,
                        'is_percentage': True,
                        'id': self.budget_category_relation1.pk
                    },
                ]
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BudgetCategoryRelation.objects.filter(budget=self.budget1).count(), 1)
        category_relation = BudgetCategoryRelation.objects.filter(budget=self.budget1).first()
        self.assertEqual(float(category_relation.amount), 6.8)
        self.assertEqual(category_relation.is_percentage, True)
        self.assertEqual(category_relation.budget.pk, self.budget1.pk)

    def test_bulk_update_replace_category_relations(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('budget_category_relation_bulk_update', kwargs={'pk': self.budget1.pk}),
            {
                'category_relations': [
                    {
                        'category': self.budget_category1.pk,
                        'amount': 35,
                        'is_percentage': True,
                    },
                ]
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BudgetCategoryRelation.objects.filter(budget=self.budget1).count(), 1)
        category_relation = BudgetCategoryRelation.objects.filter(budget=self.budget1).first()
        self.assertEqual(float(category_relation.amount), 35)
        self.assertEqual(category_relation.is_percentage, True)
        self.assertNotEqual(category_relation.pk, self.budget_category_relation1.pk)

    def test_get_planned_actual_spending_valid(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(reverse('planned_actual_spending', kwargs={
            'pk': self.budget1.pk
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cant_get_planned_actual_spending_other_users_budget(self):
        self.client.login(username='user2', password='password2')
        response = self.client.get(reverse('planned_actual_spending', kwargs={
            'pk': self.budget1.pk
        }))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_planned_spending_unauthorized(self):
        response = self.client.get(reverse('planned_actual_spending', kwargs={
            'pk': self.budget1.pk
        }))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
