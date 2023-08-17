from datetime import datetime
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from expenses.models import *
from users.models import User
from utils.choices import *


class ExpensesTest(TestCase):
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
        cls.expense1 = Expense.objects.create(
            name='Expense 1',
            category=cls.budget_category1,
            timestamp=datetime.now(tz=timezone.utc),
            amount=50.00,
            user=cls.user1,
        )
        cls.expense2 = Expense.objects.create(
            name='Expense 2',
            category=cls.budget_category1,
            timestamp=datetime.now(tz=timezone.utc),
            amount=120.00,
            user=cls.user2,
        )

    def test_create_expense(self):
        self.client.login(username='user1', password='password1')
        response = self.client.post(
            reverse('expense_list'),
            {
                'name': 'New Expense',
                'category': self.budget_category3.pk,
                'timestamp': datetime.now(tz=timezone.utc),
                'amount': 45.56,
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['name'], 'New Expense')
        self.assertEqual(response.json()['user']['username'], 'user1')

    def test_list_expenses(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expense_list')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1) # Only this user's expense
        self.assertEqual(response.json()['results'][0]['id'], self.expense1.pk)

    def test_list_expenses_category_filter_exact(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expense_list'),
            {'category': self.budget_category2.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

        response = self.client.get(
            reverse('expense_list'),
            {'category': self.budget_category1.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['id'], self.expense1.pk)

    def test_list_expenses_category_filter_list(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expense_list'),
            {'category__in': [self.budget_category2.pk, self.budget_category3.pk]}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 0)

        response = self.client.get(
            reverse('expense_list'),
            {'category__in': f'{self.budget_category1.pk},{self.budget_category2.pk}'}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['id'], self.expense1.pk)

    def test_cant_retrieve_other_users_expense(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expense_detail', kwargs={
                'pk': self.expense2.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_own_expense(self):
        self.client.login(username='user2', password='password2')
        response = self.client.get(
            reverse('expense_detail', kwargs={
                'pk': self.expense2.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['user']['id'], self.user2.pk)
        self.assertEqual(float(response.json()['amount']), self.expense2.amount)

    def test_edit_expense(self):
        self.client.login(username='user1', password='password1')
        response = self.client.patch(
            reverse('expense_detail', kwargs={
                'pk': self.expense1.pk
            }),
            {
                'name': 'New Expense Name'
            },
            'application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['name'], 'New Expense Name')
        self.assertEqual(Expense.objects.get(pk=self.expense1.pk).name, 'New Expense Name')

    def test_delete_expense(self):
        self.client.login(username='user1', password='password1')
        response = self.client.delete(
            reverse('expense_detail', kwargs={
                'pk': self.expense1.pk
            })
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(Expense.objects.first().pk, self.expense2.pk)

    def test_get_expenses_by_category(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expenses_by_category')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 3)
        self.assertEqual(response.json()['results'][0]['id'], self.budget_category1.pk)
        self.assertEqual(response.json()['results'][0]['total_amount'], self.expense1.amount)
        self.assertEqual(response.json()['results'][1]['id'], self.budget_category2.pk)
        self.assertEqual(response.json()['results'][1]['total_amount'], 0)
        self.assertEqual(response.json()['results'][2]['id'], self.budget_category3.pk)
        self.assertEqual(response.json()['results'][2]['total_amount'], 0)

    def test_get_expenses_by_category_multiple(self):
        Expense.objects.create(
            name='Expense 2',
            category=self.budget_category2,
            timestamp=datetime.now(tz=timezone.utc),
            amount=85.00,
            user=self.user1
        )
        Expense.objects.create(
            name='Expense 2',
            category=self.budget_category2,
            timestamp=datetime.now(tz=timezone.utc),
            amount=106.00,
            user=self.user1
        )
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expenses_by_category')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['count'], 3)

        # Sorted highest to lowest
        self.assertEqual(float(response.json()['results'][0]['total_amount']), 191)
        self.assertEqual(float(response.json()['results'][1]['total_amount']), 50)
        self.assertEqual(float(response.json()['results'][2]['total_amount']), 0)
        self.assertEqual(response.json()['results'][0]['id'], self.budget_category2.pk)
        self.assertEqual(response.json()['results'][1]['id'], self.budget_category1.pk)
        self.assertEqual(response.json()['results'][2]['id'], self.budget_category3.pk)

    def test_get_expenses_csv(self):
        self.client.login(username='user1', password='password1')
        response = self.client.get(
            reverse('expenses_csv_export')
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

