from django.forms import ModelForm
from .models import AuctionListing, Comment, Bid
from django import forms
from django.core.exceptions import ValidationError


# general function to style forms to inheret from here instead of default forms
class StylishForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})


# form to create a new listing
class NewListing(StylishForm):
    listing_image = forms.ImageField(required=False)

    class Meta:
        model = AuctionListing
        fields = [
            "title",
            "description",
            "price",
            "min_bid",
            "category",
            "listing_image",
            "auction_item",
        ]


# form for new page entry
class ListingComment(StylishForm):
    class Meta:
        model = Comment
        fields = ["comment_owner", "comment_title", "comment_input"]


class BidsForm(StylishForm):
    class Meta:
        model = Bid
        fields = ["bidder", "bid_input"]
        # to hide field from html
        widgets = {
            "bidder": forms.HiddenInput(),
        }
        ordering = ["-bid_input"]


class EndListing(StylishForm):
    class Meta:
        model = AuctionListing
        fields = ["title", "inactive"]
