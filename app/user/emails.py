from django.core.mail import send_mail
import random
from .models import CustomUser


def send_otp_email(email):
    subject = 'Your account verification email'
    otp = random.randint(100000, 999999)
    message = f'Your OTP is {otp}'
    email_from = 'chromweechannelusa@gmail.com'
    send_mail(subject, message, email_from, [email,])
    user_obj = CustomUser.objects.get(email=email)
    user_obj.otp = otp
    user_obj.save()