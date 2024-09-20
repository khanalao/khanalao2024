import random
import string
import time
from datetime import datetime


def generate_order_number(pk):
    current_datetime = datetime.now().strftime('%Y%m%d%H%M%S')  # 20220616233810 + pk
    order_number = current_datetime + str(pk)
    return order_number


def generate_transaction_id():
    # Generate random letters and digits
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    # Use current timestamp to ensure uniqueness
    timestamp = str(int(time.time()))  # Convert current time to a string

    # Combine the random part and timestamp to form the transaction ID
    transaction_id = random_part + timestamp

    return transaction_id