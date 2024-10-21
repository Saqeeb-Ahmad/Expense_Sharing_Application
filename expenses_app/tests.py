from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from .models import Expense
from .serializers import ExpenseSerializer
import json

User = get_user_model()

class ModelTests(TestCase):
    def test_create_user(self):
        """Test creating a new user"""
        email = 'test@example.com'
        password = 'testpass123'
        name = 'Test User'
        user = User.objects.create_user(
            email=email,
            password=password,
            name=name
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.name, name)

    def test_create_expense(self):
        """Test creating a new expense"""
        user = User.objects.create_user(email='test@example.com', password='testpass123', name='Test User')
        expense = Expense.objects.create(
            total_amount=Decimal('100.00'),
            split_method='equal',
            created_by=user,
            category='Food',
            split_details={}
        )
        expense.participants.add(user)
        self.assertEqual(expense.total_amount, Decimal('100.00'))
        self.assertEqual(expense.created_by, user)
        self.assertEqual(expense.participants.count(), 1)

class SerializerTests(TestCase):
    def test_expense_serializer(self):
        """Test the expense serializer"""
        user = User.objects.create_user(email='test@example.com', password='testpass123', name='Test User')
        expense_data = {
            'total_amount': '100.00',
            'split_method': 'equal',
            'category': 'Food',
            'participants': [user.id],
            'split_details': {str(user.id): '100.00'}
        }
        serializer = ExpenseSerializer(data=expense_data)
        self.assertTrue(serializer.is_valid())

class ViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', password='testpass123', name='Test User')
        self.client.force_authenticate(user=self.user)

    def test_create_expense(self):
        """Test creating an expense through the API"""
        payload = {
            'total_amount': '100.00',
            'split_method': 'equal',
            'category': 'Food',
            'participants': [self.user.id],
            'split_details': json.dumps({str(self.user.id): '100.00'})
        }
        res = self.client.post('/api/expenses/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(id=res.data['id'])
        self.assertEqual(expense.total_amount, Decimal('100.00'))
        self.assertEqual(expense.participants.count(), 1)

    def test_retrieve_expenses(self):
        """Test retrieving a list of expenses"""
        expense1 = Expense.objects.create(
            total_amount='100.00',
            split_method='equal',
            created_by=self.user,
            category='Food',
            split_details={}
        )
        expense1.participants.add(self.user)

        expense2 = Expense.objects.create(
            total_amount='200.00',
            split_method='equal',
            created_by=self.user,
            category='Transport',
            split_details={}
        )
        expense2.participants.add(self.user)

        res = self.client.get('/api/expenses/user/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_generate_balance_sheet(self):
        """Test generating a balance sheet"""
        expense = Expense.objects.create(
            total_amount='100.00',
            split_method='equal',
            created_by=self.user,
            category='Food',
            split_details={}
        )
        expense.participants.add(self.user)

        res = self.client.get('/api/balance-sheet/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/csv')