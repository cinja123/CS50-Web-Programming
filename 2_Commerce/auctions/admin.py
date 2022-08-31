from django.contrib import admin

from .models import User, Categories, Auction_Listing, Bids, Comments, Watchlist

# Register your models here.

admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Auction_Listing)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Watchlist)