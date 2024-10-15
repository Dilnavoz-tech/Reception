from django.contrib import admin
from .models import User, BlacklistedAccessToken


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'is_deleted', 'role')
    list_display_links = ('id', 'username', 'role')


class BlacklistedAccessTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'blacklisted_at')
    list_display_links = ('id', 'token', 'blacklisted_at')


admin.site.register(User, UserAdmin)
admin.site.register(BlacklistedAccessToken)
