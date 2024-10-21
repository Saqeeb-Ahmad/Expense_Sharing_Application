from django.urls import path
from .views import LoginView, GenerateTokenView,UserCreateView, UserRetrieveView, ExpenseCreateView, UserExpensesView, OverallExpensesView, BalanceSheetView, UserBalanceView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('generate-token/', GenerateTokenView.as_view(), name='generate-token'),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('users/<int:pk>/', UserRetrieveView.as_view(), name='user-retrieve'),
    path('expenses/', ExpenseCreateView.as_view(), name='expense-create'),
    path('expenses/user/', UserExpensesView.as_view(), name='user-expenses'),
    path('expenses/overall/', OverallExpensesView.as_view(), name='overall-expenses'),
    path('balance-sheet/', BalanceSheetView.as_view(), name='balance-sheet'),
    
]