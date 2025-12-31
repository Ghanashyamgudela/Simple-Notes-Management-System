from itsdangerous import URLSafeTimedSerializer
salt='otpverify'
secret_key='Code$code1234'
def endata(data):
    serialier=URLSafeTimedSerializer(secret_key)
    return serialier.dumps(data,salt=salt)

def dndata(data):
    serialier=URLSafeTimedSerializer(secret_key)
    return serialier.loads(data,salt=salt)