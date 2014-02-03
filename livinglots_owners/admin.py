from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .admin_views import MakeAliasesView
from .models import Alias


class OwnerAdminMixin(object):
    actions = ('make_aliases',)

    def aliases_summary(self, obj):
        return ', '.join(obj.aliases.all().values_list('name', flat=True))
    aliases_summary.short_description = 'AKA'

    def make_aliases(self, request, queryset):
        ids = queryset.values_list('pk', flat=True)
        ids = [str(id) for id in ids]
        return HttpResponseRedirect(reverse('admin:owners_owner_make_aliases') +
                                    '?ids=%s' % (','.join(ids)))

    def get_urls(self):
        opts = self.model._meta
        app_label, object_name = (opts.app_label, opts.object_name.lower())
        prefix = "%s_%s" % (app_label, object_name)

        urls = super(OwnerAdminMixin, self).get_urls()
        my_urls = patterns('',
            url(r'^make-aliases/', MakeAliasesView.as_view(),
                name='%s_make_aliases' % prefix),
        )
        return my_urls + urls


class BaseOwnerAdmin(OwnerAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'owner_type', 'aliases_summary',)
    search_fields = ('name',)


class AliasAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Alias, AliasAdmin)
