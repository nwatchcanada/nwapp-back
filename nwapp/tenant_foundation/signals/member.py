from django.db.models.signals import post_save
from django.dispatch import receiver

from tenant_foundation.models import Member, UnifiedSearchItem


@receiver(post_save, sender=Member)
def save_member(sender, instance, **kwargs):
    """
    Function will either update or create the `UnifiedSearchItem` object so
    we have a unified searchable record for all our data.
    """
    print("SIGNAL: save_member") # For debugging purposes only.
    UnifiedSearchItem.objects.update_or_create_member(instance)


@receiver(post_save, sender=Member)
def save_member_user(sender, instance, **kwargs):
    """
    Function will update the user profile with the member's fields post save.
    """
    print("SIGNAL: save_member_user") # For debugging purposes only.
    pass


@receiver(post_save, sender=Member)
def invalidate_member_cache(sender, instance, **kwargs):
    """
    Clear the member's cache post save.
    """
    print("SIGNAL: invalidate_member_cache") # For debugging purposes only.
    instance.invalidate_all()
