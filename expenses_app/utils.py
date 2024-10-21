from decimal import Decimal

def calculate_split(total_amount, split_method, split_details, participants):
    if split_method == 'equal':
        share = total_amount / len(participants)
        return {str(user.id): str(share) for user in participants}
    elif split_method == 'exact':
        return split_details
    elif split_method == 'percentage':
        return {
            user_id: str(Decimal(percent) / 100 * total_amount)
            for user_id, percent in split_details.items()
        }
    else:
        raise ValueError("Invalid split method")

def validate_split_details(total_amount, split_method, split_details, participants):
    if split_method == 'equal':
        return True
    elif split_method == 'exact':
        total_split = sum(Decimal(amount) for amount in split_details.values())
        return total_split == total_amount
    elif split_method == 'percentage':
        total_percentage = sum(Decimal(percent) for percent in split_details.values())
        return total_percentage == 100
    else:
        return False