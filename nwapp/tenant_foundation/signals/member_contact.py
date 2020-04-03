from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import MemberContact


@receiver(post_save, sender=MemberContact)
def save_member_contact_user(sender, instance, **kwargs):
    """
    Function will update the user profile with the member's fields post save.
    """
    print("SIGNAL: save_member_contact_user") # For debugging purposes only.
    instance.member.user.first_name = instance.first_name
    instance.member.user.last_name = instance.last_name
    instance.member.user.email = instance.email
    instance.member.user.save()


@receiver(post_save, sender=MemberContact)
def invalidate_member_contact_cache(sender, instance, **kwargs):
    """
    Clear the member contact's cache post save.
    """
    print("SIGNAL: invalidate_member_contact_cache") # For debugging purposes only.
    instance.invalidate_all()
