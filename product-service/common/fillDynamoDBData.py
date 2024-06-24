import boto3
import uuid
import os

products_table_name = os.getenv('PRODUCTS_TABLE_NAME', "products")
stocks_table_name = os.getenv('STOCKS_TABLE_NAME', "stocks")

def get_input():
    title = input("Enter product title: ").strip()
    description = input("Enter product description: ").strip()
    price = input("Enter product price: ").strip()
    count = input("Enter product count: ").strip()
    confirm = input("Is the information correct? (y/n) ").strip()
    if confirm == 'y':
        tableCreation(title, description, price, count)
    else:
        get_input()
    cont = input("Would you like to add a new product? (y/n) ").strip()
    if cont == 'y':
        get_input()
    else:
        print("Goodbye!")
        return "Goodbye!"


def tableCreation(title, description, price, count=0):
    try:
        id = uuid.uuid4()

        dynamodb = boto3.client('dynamodb')
        response = dynamodb.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': products_table_name,
                        'Item': {
                            'id': {'S': str(id)},
                            'title': {'S': str(title)},
                            'description': {'S': str(description)},
                            'price': {'N': str(price)},
                        },
                        'ConditionExpression': 'attribute_not_exists(id)',
                        'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                    }
                },
                {
                    'Put': {
                        'TableName': stocks_table_name,
                        'Item': {
                            'product_id': {'S': str(id)},
                            'count': {'N': str(count)},
                        },
                        'ConditionExpression': 'attribute_not_exists(product_id)',
                        'ReturnValuesOnConditionCheckFailure': 'ALL_OLD'
                    }
                }
            ]
        )

        print(f"Table {title} was created")
    except Exception as e:
        print(f"Failed to create table '{title}': {e}")

if __name__ == "__main__":
    get_input()