from autocomplete_light.autocomplete.shortcuts import AutocompleteModelBase
from autocomplete_light.registry import register

from livinglots import get_owner_model, get_owner_contact_model


class AdminAutocomplete(AutocompleteModelBase):

    def choices_for_request(self):
        choices = super(AdminAutocomplete, self).choices_for_request()
        if not self.request.user.is_staff:
            choices = choices.none()
        return choices


class OwnerAutocomplete(AdminAutocomplete):
    autocomplete_js_attributes = {'placeholder': 'Owner name',}
    search_fields = ('name',)


class OwnerContactAutocomplete(AdminAutocomplete):
    autocomplete_js_attributes = {'placeholder': 'Owner contact',}
    search_fields = ('name',)


register(get_owner_model(), OwnerAutocomplete)
register(get_owner_contact_model(), OwnerContactAutocomplete)
