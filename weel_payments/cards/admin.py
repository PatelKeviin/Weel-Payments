from django.contrib import admin

from .models import Card, CardControl, Transaction


admin.site.register(Card)
admin.site.register(CardControl)
admin.site.register(Transaction)
