from django import forms
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.generic import FormView

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from dal import autocomplete
from livinglots import get_owner_model
from livinglots_forms.widgets import AddAnotherWidgetWrapper


class MakeAliasesForm(forms.Form):
    owner = forms.ModelChoiceField(
        # NB, does not exclude owners_to_delete
        queryset=get_owner_model().objects.all().order_by('name'),
        widget=autocomplete.ModelSelect2('owners:owner-autocomplete')
    )

    owners_to_delete = forms.ModelMultipleChoiceField(
        queryset=get_owner_model().objects.all(),
        widget=forms.MultipleHiddenInput(),
    )


class MakeAliasesView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = MakeAliasesForm
    permission_required = ('owners.add_owner', 'owners.delete_alias',)
    template_name = 'admin/owners/owner/make_aliases.html'

    def get_context_data(self, **kwargs):
        context = super(MakeAliasesView, self).get_context_data(**kwargs)
        context.update({
            'is_popup': False,
            'opts': get_owner_model()._meta,
            'title': _('Make Aliases'),
            'owners_to_delete': get_owner_model().objects.filter(
                pk__in=self.request.GET.get('ids', '').split(','),
            ).order_by('name'),
        })
        return context

    def get_initial(self):
        initial = super(MakeAliasesView, self).get_initial()
        initial.update({
            'owners_to_delete': get_owner_model().objects.filter(
                pk__in=self.request.GET.get('ids', '').split(','),
            ),
        })
        return initial

    def get_success_url(self):
        return reverse('admin:owners_owner_changelist')

    def form_valid(self, form):
        owner = form.cleaned_data['owner']
        owners_to_delete = form.cleaned_data['owners_to_delete']
        aliases_added = owners_to_delete.count()

        self._make_aliases(owner, owners_to_delete)

        messages.success(self.request,
                         'Added %d aliases to %s' % (aliases_added, owner.name))
        return super(MakeAliasesView, self).form_valid(form)

    def _make_aliases(self, owner, owners_to_delete):
        """
        Create aliases for the given owner and move related objects to it, then
        delete the aliased owners.
        """
        for owner_to_delete in owners_to_delete:
            owner.make_alias(owner_to_delete)
