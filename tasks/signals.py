from .models import ForceMember, PresentAddress, PermanentAddress, MiRoomVisit, Duty, Ro
from django.db.models.signals import post_save,pre_save,post_delete 
from django.dispatch import receiver 
from django.core.mail import send_mail


@receiver(post_save, sender=ForceMember)
def notify_ForceMember_on_creation(sender, instance, created, **kwargs):
    # print("signal call = ",created)
    if not created:
        return   # update হলে কিছু করবে না
    # print("Email will be sent to :",instance.email)
    emails = [instance.email]  # single email → list বানানো

    send_mail(
        subject='New Force Member Created and save',
        message=f'{instance.name} has been added in Bn HQ',
        from_email="faridali9818@gmail.com",
        recipient_list=emails,
        fail_silently=False,
    )


@receiver(post_delete, sender=ForceMember)
def delete_forcemember(sender, instance, **kwargs):
    # print("SIGNAL HIT")

    if hasattr(instance, 'present_address'):
        instance.present_address.delete()

    if hasattr(instance, 'permanent_address'):
        instance.permanent_address.delete()

    # print(f"ForceMember deleted: {instance.name} ({instance.no})")
    # print(f"All related data deleted for {instance.name}")


11.4