from yoomoney import Quickpay, Client

YOOMONEY_TOKEN = "your yoomoney token"

def create_payment(user_id, amount: float = 10):
    label = str(user_id)
    quickpay = Quickpay(
        receiver="your receiver",
        quickpay_form="example",
        targets="example",
        paymentType="SB",
        sum=amount,
        label=label
    )
    return quickpay.base_url, label

def check_payment(label, expected_amount: float):
    client = Client(YOOMONEY_TOKEN)
    history = client.operation_history(label=label)
    tolerance = expected_amount * 0.97

    for operation in history.operations:
        if operation.status == 'success' and operation.label == label and operation.amount >= tolerance:
            return True
    return False