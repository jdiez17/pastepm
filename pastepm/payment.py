from paypal import PayPalConfig, PayPalInterface

from config import config

using_paypal = config.has_section('paypal')
paypal = None

if using_paypal:
    paypal_config = PayPalConfig(
        API_USERNAME=config.get('paypal', 'username'),
        API_PASSWORD=config.get('paypal', 'password'),
        API_SIGNATURE=config.get('paypal', 'signature)
    )

    paypal = PayPalInterface(config=paypal_config) 
