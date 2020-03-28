from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import Member


@receiver(post_save, sender=Member)
def save_member_user(sender, instance, **kwargs):
    """
    Function will update the user profile with the member's fields post save.
    """
    pass


@receiver(post_save, sender=Member)
def invalidate_member_cache(sender, instance, **kwargs):
    """
    Clear the member's cache post save.
    """
    instance.invalidate_all()
