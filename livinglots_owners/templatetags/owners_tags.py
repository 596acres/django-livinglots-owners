from django import template
from django.core.cache import cache

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag

from livinglots import get_lot_model, get_owner_model

register = template.Library()


class GetOwners(AsTag):
    options = Options(
        'type',
        Argument('owner_type', required=True, resolve=True),
        Argument('visible_only', required=False, resolve=True),
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def fetch_owners(self, owner_type, visible_only=True):
        """Get owners from database"""
        owners = get_owner_model().objects.filter(
            owner_type=owner_type
        ).order_by('name')

        if visible_only:
            owners = [o for o in owners if get_lot_model().visible.filter(owner=o).exists()]
        return owners


    def get_owners(self, owner_type, visible_only=True):
        """Get owners from cache or fetch from database and store in cache"""
        cache_key = 'owner_tags:get_owners:%s:%s' % (owner_type, str(visible_only))
        owners = cache.get(cache_key)
        if not owners:
            owners = self.fetch_owners(owner_type, visible_only=visible_only)
            cache.set(cache_key, owners, 30 * 60)
        return owners

    def get_value(self, context, owner_type, visible_only):
        return self.get_owners(owner_type, visible_only=visible_only)


register.tag(GetOwners)
