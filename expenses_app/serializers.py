from rest_framework import serializers
from .models import Expense, User
from decimal import Decimal
from .utils import calculate_split, validate_split_details

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    
    This serializer handles the serialization and deserialization of User objects,
    including user creation with password hashing.
    """
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'mobile','password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
        Create and return a new User instance, given the validated data.
        
        This method is used for user registration, ensuring that the password
        is properly hashed before saving the user object.
        
        :param validated_data: Dictionary of validated user data
        :return: Newly created User instance
        """
        
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            name=validated_data['name'],
            mobile=validated_data['mobile'],
            password=validated_data['password'] 
        )
        return user
class ExpenseSerializer(serializers.ModelSerializer):
    """
    Serializer for the Expense model.
    
    This serializer handles the serialization and deserialization of Expense objects,
    including complex validation for different split methods.
    """
    
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    split_details = serializers.JSONField(required=False)

    class Meta:
        model = Expense
        fields = ['id', 'total_amount', 'split_method', 'created_by', 'participants', 'split_details', 'category', 'created_at']
        read_only_fields = ['created_by', 'created_at']

    def validate(self, data):
        """
        Validate the expense data, particularly the split method and details.
        
        This method performs complex validation based on the chosen split method:
        - For 'equal' split, it calculates equal shares for all participants.
        - For 'exact' split, it ensures the sum of split amounts equals the total.
        - For 'percentage' split, it ensures percentages sum to 100 and calculates amounts.
        
        It also uses external validation functions for additional checks.
        
        :param data: Dictionary of input data
        :return: Validated and potentially modified data dictionary
        """
        
        split_method = data['split_method']
        total_amount = data['total_amount']
        participants = data['participants']
        split_details = data.get('split_details', {})

        # Validation logic for different split method
        if split_method == 'equal':
            share = total_amount / len(participants)
            data['split_details'] = {str(user.id): str(share) for user in participants}
        elif split_method == 'exact':
            if not split_details:
                raise serializers.ValidationError("Split details are required for exact split")
            total_split = sum(Decimal(amount) for amount in split_details.values())
            if total_split != total_amount:
                raise serializers.ValidationError("The sum of split amounts must equal the total amount")
        elif split_method == 'percentage':
            if not split_details:
                raise serializers.ValidationError("Split details are required for percentage split")
            total_percentage = sum(Decimal(percent) for percent in split_details.values())
            if total_percentage != 100:
                raise serializers.ValidationError("The sum of percentages must equal 100")
            data['split_details'] = {
                user_id: str(Decimal(percent) / 100 * total_amount)
                for user_id, percent in split_details.items()
            }
            
        # Additional validation using external functions
        if not validate_split_details(total_amount, split_method, split_details, participants):
            raise serializers.ValidationError("Invalid split details")

        # Calculate the final split details
        data['split_details'] = calculate_split(total_amount, split_method, split_details, participants)

        return data

    def create(self, validated_data):
        """
        Create and return a new Expense instance, given the validated data.
        
        This method handles the creation of an Expense object and associates
        the participants with the expense.
        
        :param validated_data: Dictionary of validated expense data
        :return: Newly created Expense instance
        """
        participants = validated_data.pop('participants')
        expense = Expense.objects.create(**validated_data)
        expense.participants.set(participants)
        return expense