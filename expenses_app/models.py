from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    This model adds additional fields to the default User model:
    - email: Used as the unique identifier for authentication
    - name: Full name of the user
    - mobile: Mobile number of the user
    """
    
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        """
        String representation of the User model.
        
        :return: User's email address
        """
        return self.email

# Get the custom User model
User = get_user_model()

class Expense(models.Model):
    """
    Model to represent an expense in the system.
    
    This model stores information about individual expenses, including:
    - The total amount of the expense
    - The method used to split the expense
    - Who created the expense
    - The participants involved in the expense
    - Details of how the expense is split
    - The category of the expense
    - When the expense was created
    """
    
    SPLIT_CHOICES = [
        ('equal', 'Equal'),
        ('exact', 'Exact'),
        ('percentage', 'Percentage'),
    ]

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    split_method = models.CharField(max_length=10, choices=SPLIT_CHOICES)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_expenses')
    participants = models.ManyToManyField(User, related_name='expenses')
    split_details = models.JSONField()
    category = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    split_details = models.JSONField()

    def __str__(self):
        """
        String representation of the Expense model.
        
        :return: A string describing the expense amount and creator
        """
        
        return f"Expense of {self.total_amount} created by {self.created_by}"