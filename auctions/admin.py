from django.contrib import admin
from .models import *


# Register your models here.
# classes to change view on admin page
class UserAdmin(admin.ModelAdmin):
    pass

class WatchListAdmin(admin.ModelAdmin):
    filter_horizontal = ["listingitems"]


class AuctionListingAdmin(admin.ModelAdmin):
    list_display = ["title", "owner"]

class BidsAdmin(admin.ModelAdmin):
    list_display = ["bid_input", "bidder", "listing_bids"]

class CommentAdmin(admin.ModelAdmin):
    list_display = ["comment_owner", "comment_created", "comment_input", "listing_comments"]

admin.site.register(User, UserAdmin)
admin.site.register(WatchList, WatchListAdmin)
admin.site.register(AuctionListing, AuctionListingAdmin)
admin.site.register(Bid, BidsAdmin)
admin.site.register(Comment, CommentAdmin)