from django import template

from classytags.arguments import Argument
from classytags.core import Options
from classytags.helpers import AsTag

from livinglots import get_owner_model

register = template.Library()


class GetOwners(AsTag):
    options = Options(
        'type',
        Argument('owner_type', required=True, resolve=True),
        'as',
        Argument('varname', required=True, resolve=False),
    )

    def get_value(self, context, owner_type):
        return get_owner_model().objects.filter(
            owner_type=owner_type
        ).order_by('name')


register.tag(GetOwners)
