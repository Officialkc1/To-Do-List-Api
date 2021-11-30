from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


@receiver(post_save, sender=User)
def post_save_generate_code(sender, instance, created, *args, **kwargs):
    if created:
        message = f""""Hello, {instance.first_name}.
Thank you for signing up on our platform. We are very glad!
Regards,
The Django Team.
        """
        send_mail(subject="Your Account has been created successfully",
                message=message,
                recipient_list=[instance.email],
                from_email="kiherome@gmail.com")