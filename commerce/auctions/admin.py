from django.contrib import admin
from  .models import Auction_listings, Bids, Comments
# Register your models here.

admin.site.register(Auction_listings)
admin.site.register(Bids)
admin.site.register(Comments)