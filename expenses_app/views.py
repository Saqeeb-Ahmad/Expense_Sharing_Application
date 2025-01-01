from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import ExpenseSerializer
from rest_framework import serializers
from django.db import transaction
from django.http import HttpResponse
from rest_framework.views import APIView
from .models import Expense, User
import csv
from decimal import Decimal
from django.db.models import Sum, F, Q
from rest_framework.authtoken.models import Token
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict
from io import BytesIO, StringIO
from django.db.models import Sum, Min, Max


# Create your views here.
class LoginView(APIView):
    """
    API View for user login.
    
    This view handles POST requests for user authentication.
    It expects an email and password in the request data.
    
    If authentication is successful, it returns an authentication token.
    If authentication fails, it returns an error message.
    """
    def post(self, request):
        """
        Handle POST request for user login.
        
        :param request: The HTTP request object
        :return: Response with token if login successful, error message otherwise
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
         # Validate input
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user:
            # Generate or retrieve token for authenticated user
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
             # Authentication failed
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class GenerateTokenView(APIView):
    """
    API View for generating authentication tokens.
    
    This view handles POST requests to generate or retrieve an authentication token for a user.
    It expects an email and password in the request data.
    
    If authentication is successful, it returns the token along with user details.
    If authentication fails, it returns an error message.
    """
    
    def post(self, request):
        """
        Handle POST request to generate or retrieve an authentication token.
        
        :param request: The HTTP request object
        :return: Response with token and user details if successful, error message otherwise
        """
        
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Validate input
        if not email or not password:
            return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate user
        user = authenticate(request, username=email, password=password)
        
        if user:
            # Generate or retrieve token for authenticated user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserCreateView(generics.CreateAPIView):
    """
    API View for creating new users.
    
    This view handles POST requests to create a new user account.
    It uses the User model and UserSerializer for data validation and creation.
    No authentication is required to access this view (AllowAny permission).
    
    Upon successful user creation, it generates an authentication token for the new user.
    """
    
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Handle POST request to create a new user.
        
        This method overrides the default create method to generate
        an authentication token upon successful user creation.
        
        :param request: The HTTP request object
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        :return: Response with user data and token if creation successful
        """
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token for the newly created user
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class UserRetrieveView(generics.RetrieveAPIView):
    """
    API View for retrieving user details.
    
    This view handles GET requests to retrieve details of a specific user.
    It uses the User model and UserSerializer to fetch and serialize user data.
    
    The view is based on Django REST Framework's RetrieveAPIView, which
    provides read-only access to a single model instance.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Note: No custom methods are defined here as the default
    # behavior of RetrieveAPIView is sufficient for this use case.
    # It will automatically handle GET requests to fetch a single user
    # based on the provided primary key (pk) in the URL.
    

class ExpenseCreateView(generics.CreateAPIView):
    """
    API View for creating new expenses.
    
    This view handles POST requests to create a new expense.
    It uses the ExpenseSerializer for data validation and creation.
    Only authenticated users can access this view (IsAuthenticated permission).
    """
    
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Custom method to perform the creation of a new expense.
        
        This method is called by CreateAPIView when saving the new expense instance.
        It sets the created_by field to the current user and handles the association
        of participants with the expense.
        
        :param serializer: The validated serializer instance
        """
        
        # Save the expense with the current user as the creator
        expense = serializer.save(created_by=self.request.user)
        
        # Get the list of participant IDs from the request data
        participants = self.request.data.get('participants', [])
        
         # Ensure the creator is also a participant
        if self.request.user.id not in participants:
            participants.append(self.request.user.id)
        
         # Add all participants to the expense
        expense.participants.add(*participants)




class UserExpensesView(generics.ListAPIView):
    """
    API View for retrieving a list of expenses for the authenticated user.
    
    This view handles GET requests to fetch all expenses associated with the current user.
    Only authenticated users can access this view (IsAuthenticated permission).
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        
        """
        Custom method to handle GET requests for user expenses.
        
        This method overrides the default list method to provide a custom
        response format with detailed expense information.
        
        :param request: The HTTP request object
        :param args: Additional positional arguments
        :param kwargs: Additional keyword arguments
        :return: Response with a list of expense data for the user
        """
        
        user = request.user
        expenses = Expense.objects.filter(participants=user)

        expense_data = []
        for expense in expenses:
            # Prepare participant data, excluding the current user
            participants = []
            for participant in expense.participants.exclude(id=user.id):
                participants.append({
                    "id": participant.id,
                    "name": participant.name or f"User {participant.id}",
                    "email": participant.email,
                    "share": Decimal(expense.split_details.get(str(participant.id), 0))
                })
            # Compile expense details
            expense_data.append({
                "expense_id": expense.id,
                "category": expense.category,
                "total_amount": expense.total_amount,
                "split_method": expense.split_method,
                "your_share": Decimal(expense.split_details.get(str(user.id), 0)),
                "participants": participants
            })

        return Response(expense_data)
    
    
    def get_queryset(self):
        """
        Get the list of expenses for the current user.
        
        :return: QuerySet of Expense objects associated with the current user
        """
        return Expense.objects.filter(participants=self.request.user)
    
class OverallExpensesView(generics.ListAPIView):
    
    """
    API View for retrieving a list of all expenses in the system.
    
    This view handles GET requests to fetch all expenses, regardless of the user.
    Only authenticated users can access this view (IsAuthenticated permission).
    
    It uses the ExpenseSerializer to serialize the expense data.
    """
    
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Expense.objects.all()
    # Note: This class uses the default implementation of ListAPIView
    # It will return all expenses in the system, serialized using ExpenseSerializer
    # The queryset is set to retrieve all Expense objects
    # Additional filtering or ordering could be added by overriding get_queryset() if needed
     
class BalanceSheetView(APIView):
    """
    API View for generating a detailed balance sheet as a CSV file.
    
    This view handles GET requests to create a comprehensive balance sheet
    for all users and expenses in the system. The balance sheet is returned
    as a downloadable CSV file.
    
    Only authenticated users can access this view (IsAuthenticated permission).
    """
    
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to generate the balance sheet CSV.
        
        This method retrieves all expenses and users, calculates necessary totals,
        and generates a CSV file with the following sections:
        1. Overall Expenses Summary
        2. Individual Expense Details
        3. User Balances
        
        :param request: The HTTP request object
        :return: HttpResponse with the CSV file as an attachment
        """
        
        expenses = Expense.objects.all().order_by('created_at')
        users = User.objects.all()

        # Prepare CSV data
        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # 1. Overall Expenses Summary
        total_expenses = expenses.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
        expense_count = expenses.count()
        date_range = expenses.aggregate(Min('created_at'), Max('created_at'))

        writer.writerows([
            ['Overall Expenses Summary'],
            ['Total Expenses', f'{total_expenses:.2f}'],
            ['Number of Expenses', expense_count],
            []
        ])

        # 2. Individual Expense Details
        user_names = [user.name for user in users]
        writer.writerows([
            ['Individual Expense Details'],
            ['Date', 'Description', 'Total Amount', 'Paid By', 'Split Method', 'Participants'] + [f'{name} Share' for name in user_names]
        ])

        for expense in expenses:
            participants = expense.participants.all()
            participant_shares = [f'{Decimal(expense.split_details.get(str(user.id), 0)):.2f}' for user in users]
            writer.writerow([
                expense.created_at.strftime('%Y-%m-%d'),
                expense.category,
                f'{expense.total_amount:.2f}',
                expense.created_by.name,
                expense.split_method,
                ';'.join([user.name for user in participants]),
            ] + participant_shares)

        writer.writerow([])

        # 3. User Balances 
        writer.writerows([
            ['User Balances'],
            ['User', 'Total Paid', 'Total Owed']
        ])

        for user in users:
            total_paid = expenses.filter(created_by=user).aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
            total_owed = sum(Decimal(expense.split_details.get(str(user.id), 0)) for expense in expenses)
            writer.writerow([
                user.name,
                f'{total_paid:.2f}',
                f'{total_owed:.2f}'
            ])

        # Generate CSV response
        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="detailed_balance_sheet.csv"'

        return response
        
        
class UserBalanceView(APIView):
    """
    API View for retrieving the balance summary for the authenticated user.
    
    This view handles GET requests to calculate and return the current user's
    balance with respect to all other users they have shared expenses with.
    
    Only authenticated users can access this view (IsAuthenticated permission).
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Handle GET request to retrieve the user's balance summary.
        
        This method calculates the balance between the current user and all other users
        they have shared expenses with. It considers both expenses created by the user
        and expenses where the user is a participant.
        
        :param request: The HTTP request object
        :return: Response with a dictionary of balances, where keys are user IDs and
                 values are the balance amounts (positive if owed to the current user,
                 negative if the current user owes)
        """
        
        user = request.user
        balances = {}

        # Retrieve all expenses where the user is either the creator or a participant
        expenses = Expense.objects.filter(Q(created_by=user) | Q(participants=user)).distinct()

        for expense in expenses:
            created_by = expense.created_by
            for participant_id, amount in expense.split_details.items():
                participant = User.objects.get(id=participant_id)
                if participant != user:
                    if participant not in balances:
                        balances[participant] = Decimal('0')
                    
                    # Current user paid, so others owe them
                    if created_by == user:
                        balances[participant] += Decimal(amount)
                    else:
                        # Current user owes to the expense creator
                        balances[participant] -= Decimal(amount)
        # Convert User objects to string representations in the response
        return Response({str(user): str(balance) for user, balance in balances.items()})
