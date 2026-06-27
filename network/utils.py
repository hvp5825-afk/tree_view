from .models import Referral


def find_placement_parent(sponsor, position):
    """
    Walk the binary tree from sponsor downward to find the first node
    that does NOT already have a child at the given position.
    Returns the parent User instance (or None if no placement found).
    """
    current = sponsor
    for _ in range(100):  # safety limit
        exists = Referral.objects.filter(parent=current, position=position).select_related('member').first()
        if not exists:
            return current
        current = exists.member
    return None
