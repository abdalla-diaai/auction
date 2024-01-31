from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


# lets us explicitly set upload path and filename
def upload_to(instance, filename):
    return "images/{filename}".format(filename=filename)


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    pass


class AuctionListing(TimeStampedModel):
    CHOICES = [("True", True), ("False", False)]
    owner = models.CharField(max_length=64)
    title = models.CharField(max_length=64)
    description = models.TextField()
    category = models.CharField(max_length=64)
    price = models.IntegerField()
    created = TimeStampedModel.created_at
    updated = TimeStampedModel.updated_at
    inactive = models.CharField(max_length=30, choices=CHOICES, default=False)
    listing_image = models.ImageField(upload_to="images/", blank=True)
    auction_item = models.BooleanField(null=True)
    min_bid = models.IntegerField(null=True, default=0)


class WatchList(models.Model):
    watchlist_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True
    )
    listingitems = models.ManyToManyField(
        AuctionListing, related_name="watchitems", blank=True
    )

    def __str__(self):
        return f"{self.watchlist_user}"


class Comment(TimeStampedModel):
    comment_owner = models.CharField(max_length=64, blank=True)
    comment_created = TimeStampedModel.created_at
    comment_title = models.CharField(max_length=64, blank=True)
    comment_input = models.TextField()
    listing_comments = models.ForeignKey(
        AuctionListing,
        on_delete=models.CASCADE,
        related_name="comments",
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.comment_owner} {self.comment_title} {self.comment_input}"


class Bid(TimeStampedModel):
    bid_created = TimeStampedModel.created_at
    bid_input = models.PositiveIntegerField(blank=False)
    listing_bids = models.ForeignKey(
        AuctionListing,
        on_delete=models.CASCADE,
        related_name="bids_placed",
        blank=True,
        null=True,
    )
    bidder = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True
    )

    def __str__(self) -> str:
        return f"{self.bid_input} {self.bidder}"
