from django.contrib import admin
from .models import AuctionItem, Bid, AuctionItemAdmin

# admin.site.register(AuctionItem)
admin.site.register(Bid)
admin.site.register(AuctionItem, AuctionItemAdmin)