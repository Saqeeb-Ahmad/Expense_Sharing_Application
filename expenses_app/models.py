from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager


# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    mobile = models.CharField(max_length=15)

    USERNAME_FIELD = 'email'  # Use email as the unique identifier
    REQUIRED_FIELDS = ['name']  # Additional required fields for createsuperuser

    objects = UserManager()

    def __str__(self):
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
    split_details = models.JSONField(default=dict)

    def __str__(self):
        """
        String representation of the Expense model.
        
        :return: A string describing the expense amount and creator
        """
        
        return f"Expense of {self.total_amount} created by {self.created_by}"
