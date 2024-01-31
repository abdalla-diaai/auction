from django.contrib.auth import authenticate, login, logout
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import *
from django.contrib import messages
from .forms import *
import os


def index(request):
    listings = AuctionListing.objects.all()
    active_listings = []
    inactive_listings = []
    for listing in listings:
        if listing.inactive == "False":
            active_listings.append(listing.title)
        else:
            inactive_listings.append(listing.title)
    return render(
        request,
        "auctions/index.html",
        {
            "listings": AuctionListing.objects.all(),
            "watchlist": WatchList.objects.all(),
            "username": request.user.username,
            "active_listings": active_listings,
            "inactive_listings": inactive_listings,
        },
    )


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "auctions/login.html",
                {
                    "message": "Invalid username and/or password.",
                },
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


# creating and saving new listing view
@login_required
def create(request):
    watchlist = WatchList.objects.all()
    if request.method == "POST":
        form = NewListing(request.POST, request.FILES)
        if form.is_valid():
            if "save" in request.POST:
                form.instance.owner = request.user.username
                form.save()
        return HttpResponseRedirect(reverse("index"))
    return render(
        request, "auctions/listing.html", {"form": NewListing(), "watchlist": watchlist}
    )

# viewing listing details
@login_required
def view(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    watchlist = WatchList.objects.filter(
        listingitems=listing_id, watchlist_user=request.user.pk
    )
    if watchlist.exists():
        already_exist = True
    else:
        already_exist = None
    try:
        high = listing.bids_placed.latest("bid_input")
        high_int = high.bid_input
        high_bidder = high.bidder
        watchlist = WatchList.objects.filter(pk=listing_id)

    except Bid.DoesNotExist or WatchList.DoesNotExist:
        high = 0
        high_int = 0
        high_bidder = None

    if request.method == "POST":
        form = BidsForm(request.POST, initial={"bidder": request.user.pk})
        if form.is_valid():
            if (
                form.cleaned_data["bid_input"] > high_int
                or form.cleaned_data["bid_input"] == high_int
            ) and listing.inactive == "True":
                messages.add_message(
                    request, messages.SUCCESS, f"{high_bidder} won the auction."
                )
            elif form.cleaned_data["bid_input"] > high_int:
                if form.cleaned_data["bid_input"] > listing.min_bid:
                    new_bid = form.save()
                    listing.bids_placed.add(new_bid)
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        f"Your bid ({form.cleaned_data['bid_input']}) has been successfully recorded.",
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        f"Your bid ({form.cleaned_data['bid_input']}) must be higher than minimum bid {listing.min_bid}.",
                    )
            else:
                messages.add_message(
                        request,
                        messages.ERROR,
                        f"Your bid must be higher than the previous bid {high_int}.",
                    )
            return HttpResponseRedirect(reverse("view", args=(listing.id,)))
    else:
        form = BidsForm(initial={"bidder": request.user.pk})
    return render(
        request,
        "auctions/view.html",
        {
            "listing": listing,
            "form": form,
            "high": high,
            "username": request.user.username,
            "exist": already_exist,
            "watchlist": watchlist,
        },
    )

# comment on any listing
@login_required
def comment(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    comment = listing.comments.filter(pk=listing_id)
    if request.method == "POST":
        form = ListingComment(
            request.POST, initial={"comment_owner": request.user.username}
        )
        if form.is_valid():
            comment = form.save(commit=False)
            comment.listing_comments = listing
            if "save" in request.POST:
                comment.save()
            return HttpResponseRedirect(reverse("view", args=(listing.id,)))
    else:
        form = ListingComment(initial={"comment_owner": request.user.username})
    return render(
        request,
        "auctions/comment.html",
        {
            "listing": listing,
            "comments": comment,
            "form": form,
        },
    )


@login_required
def edit(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    watchlist = WatchList.objects.all()
    if request.method == "POST":
        form = NewListing(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            # deleting old uploaded image.
            try:
                old_image_path = listing.listing_image.path
            except ValueError:
                old_image_path = ""
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
            if "save" in request.POST:
                form.save()
            return HttpResponseRedirect(reverse("index"))
    form = NewListing(instance=listing)
    return render(
        request,
        "auctions/edit.html",
        {"form": form, "listing": listing, "watchlist": watchlist},
    )

# delete a listing
@login_required
def delete(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    listing.delete()
    return HttpResponseRedirect(reverse("index"))

# add listing to watchlist
@login_required
def add_watchlist(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    watchlist, created = WatchList.objects.get_or_create(watchlist_user=request.user)
    listing.watchitems.add(watchlist)
    return render(
        request,
        "auctions/watchlist.html",
        {
            "watchlist": watchlist,
            "listing": listing,
        },
    )


@login_required
def watchlist(request):
    try:
        watchlist = WatchList.objects.get(watchlist_user=request.user)
        if watchlist.listingitems.count() == 0:
            messages.add_message(request, messages.INFO, "Watchlist is empty.")
        return render(
            request,
            "auctions/watchlist.html",
            {
                "watchlist": watchlist,
            },
        )
    except WatchList.DoesNotExist:
        messages.add_message(request, messages.INFO, "Watchlist is empty.")
        return render(
            request,
            "auctions/watchlist.html",
            {
                "watchlist": None,
            },
        )

# remove listing from watchlist
@login_required
def unwatch(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    watchlist = WatchList.objects.get(watchlist_user=request.user)
    watchlist.listingitems.remove(listing)
    return HttpResponseRedirect(reverse("watchlist"))

# categories list display
@login_required
def categories(request):
    listings = AuctionListing.objects.all()
    watchlist = WatchList.objects.all()
    categories = (
        AuctionListing.objects.values("category")
        .annotate(dcount=Count("category"))
        .order_by()
    )

    return render(
        request,
        "auctions/categories.html",
        {"categories": categories, "listings": listings, "watchlist": watchlist},
    )

# view categories
@login_required
def categories_view(request, subcat):
    listings = AuctionListing.objects.filter(category=subcat)
    watchlist = WatchList.objects.all()
    return render(
        request,
        "auctions/categories_view.html",
        {"listings": listings, "watchlist": watchlist},
    )

# end listing and give listing to highest bidder
@login_required
def end(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    if request.method == "POST":
        form = EndListing(request.POST, instance=listing)
        if form.is_valid():
            if "save" in request.POST:
                form.save()
            return HttpResponseRedirect(reverse("view", args=(listing.id,)))
    form = EndListing(instance=listing)
    return render(request, "auctions/end.html", {"form": form, "listing": listing})

# buy listing if listing not auction item
@login_required
def buy(request, listing_id):
    listing = AuctionListing.objects.get(pk=listing_id)
    listing.inactive = True
    listing.save()
    messages.add_message(
        request,
        messages.INFO,
        "Thanks for your purchase, the item will be shipped in 3-4 working days.",
    )
    return HttpResponseRedirect(reverse("view", args=(listing.id,)))
