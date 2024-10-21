# Expense_Sharing_Application
This is a Django-based RESTful API for an expense sharing application. It allows users to create and manage shared expenses, split costs among participants, and generate balance sheets.
## Features
- User registration and authentication
- Create and manage expenses
- Split expenses equally, by exact amounts, or by percentages
- View individual and overall expenses
- Generate downloadable balance sheets

## Installation
### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (recommended for creating isolated Python environments)

### Setup
1. Clone the repository:
2. Create and activate a virtual environment:
   To install environment at current directory:-
   ## pip install virtualenv
   Then to create env:- 
   ## Virtualenv  name_of_env
   To activate the env:-
   ## .\name_of_env\Scripts\activate
	then install django:-
   ## pip install django
3. Install the required packages
   ## pip install djangorestframework
4. Set up the database:-
   just do
    ## python manage.py makemigrations
    ## python manage.py migrate
   no need to do anything
6. Run the development server:-
   ## python manage.py runserver

## API Endpoints

- `/api/users/` - User registration
- `/api/generate-token/` - Generate authentication token
- `/api/login/` - User login
- `/api/users/<int:pk>/` - Retrieve user details
- `/api/expenses/` - Create expense
- `/api/expenses/user/` - List user's expenses
- `/api/expenses/overall/` - List all expenses
- `/api/balance-sheet/` - Generate balance sheet


# Testing the Expense Sharing Application with Postman
Follow these steps to test each endpoint of the application. Make sure the server is running (`python manage.py runserver`) before you start testing.
## 1. User Registration
POST http://localhost:8000/api/users/
e.g:-
Body (raw JSON):
json
{
    "email": "user1@example.com",
    "name": "User One",
    "mobile": "1234567890",
    "password": "securepassword123"
}
## User Login
POST http://localhost:8000/api/login/
{
    "email": "user1@example.com",
    "password": "securepassword123"
}
Response: You should receive a 200 OK status with an authentication token.

## Generate Token (Alternative to Login)
POST http://localhost:8000/api/generate-token/
{
    "email": "user1@example.com",
    "password": "securepassword123"
}
Response: You should receive a token and user details.

## Retrieve User Details
GET http://localhost:8000/api/users/1/
Response: You should receive the user's details.

## Create an Expense
POST http://localhost:8000/api/expenses/
e.g
{
    "total_amount": "300.00",
    "split_method": "equal",
    "participants": [1, 2, 3],
    "category": "Dinner"
}
Response: You should receive splitted expense details.

## List User's Expenses
GET http://localhost:8000/api/expenses/user/
You should receive list of the user's expenses.

## List All Expenses
GET http://localhost:8000/api/expenses/overall/
Response: You should receive list of all expenses in the system.

## Generate Balance Sheet
GET http://localhost:8000/api/balance-sheet/
Response: You should receive a Balance sheet in postman concolse to download the CSV file click on "send" buttion will get send and downlaod then donwnlaod the file in csv format.



## note after authentication token Generation Replace `your_secret_key_here`
Content-Type: application/json
Authorization: Token YOUR_AUTH_TOKEN

This is for authentication purose so that only valid user can do 
## Test these API's in Postman software
![image](https://github.com/user-attachments/assets/a9cf2f48-709d-421b-8315-caa8f2fe1fe7)


  


   


   
