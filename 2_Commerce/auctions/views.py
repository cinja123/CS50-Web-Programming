from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.validators import MinValueValidator
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from .models import User, Auction_Listing, Bids, Categories, Comments, Watchlist
from . import util

class NewListingForm(forms.Form):
    title = forms.CharField(label="Title", widget=forms.TextInput(attrs={'class': 'create title'}))
    description = forms.CharField(label="Description", widget=forms.TextInput(attrs={'class': 'create descirption'}))
    start_bid = forms.DecimalField(label="Starting Bid", min_value=0.00, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'create bid'}))
    image_url = forms.URLField(label="Image URL", required=False)
    all_categories = Categories.objects.all()
    categories = forms.ModelMultipleChoiceField(queryset=all_categories, required=False)


def index(request):
    return render(request, "auctions/index.html", {
        "auctions": Auction_Listing.objects.filter(closed=False)
    })


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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def auction_view(request, auction_id, msg=None):
    auction = util.get_auction(auction_id)
    if request.user.is_authenticated:
        try:
            if request.user.watchlist.get(auction=auction):
                in_watchlist = True
        except MultipleObjectsReturned:
            in_watchlist = True
        except ObjectDoesNotExist:
            in_watchlist = False
    else:
        in_watchlist = False 
    return render(request, "auctions/auction.html",{
        "auction": auction,
        "categories": auction.categories.all(),
        "comments": auction.comments.all(),
        "in_watchlist": in_watchlist,
        "number_watchlist": len(auction.watchlist.all()),
        "message": msg,
        "current_bid": util.get_current_bid(auction),
        "number_bids": len(auction.bids.all())
    })

@login_required(login_url='login')
def create_auction(request):
    if request.method == "POST":
        form = NewListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            start_bid = form.cleaned_data["start_bid"]
            image_url = form.cleaned_data["image_url"]
            categories = form.cleaned_data["categories"]
            new_auction = Auction_Listing(title=title, description=description, start_bid=start_bid, image_url=image_url, creator=request.user, closed=False)
            new_auction.save()
            for category in categories:
                new_auction.categories.add(category)
            return HttpResponseRedirect(reverse("auction", kwargs={'auction_id': new_auction.id}))
        else:
            return render(request, "auctions/create_auction.html", {
                "form": form
            })
    return render(request, "auctions/create_auction.html", {
        "form": NewListingForm()
    })

@login_required(login_url='login')
def watchlist_view(request):
    user = request.user
    return render(request, "auctions/watchlist.html", {
        "watchlist": user.watchlist.all()
    })

@login_required(login_url='login')
def watchlist_add(request, auction_id):
    auction = util.get_auction(auction_id)
    try:
        if request.user.watchlist.get(auction=auction):
            Watchlist.objects.filter(auction=auction, user=request.user).delete()
    except MultipleObjectsReturned:
        Watchlist.objects.filter(auction=auction, user=request.user).delete()
    except ObjectDoesNotExist:
        Watchlist.objects.create(auction=auction, user=request.user)
    return auction_view(request, auction_id)

def bid(request, auction_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        new_bid = float(request.POST["new_bid"])
        auction = util.get_auction(auction_id)
        try:
            current_bid = auction.bids.get(highest=True)
        except ObjectDoesNotExist:
            current_bid = -1

        if (current_bid == -1) and (new_bid >= float(auction.start_bid)):
            Bids.objects.create(bid=new_bid, bid_user=request.user, auction=auction, highest=True)
        elif (current_bid == -1):
            return auction_view(request, auction_id, msg=f"Your bid has to be at least $ {auction.start_bid}.")
        elif float(current_bid.bid) < new_bid:
            auction.bids.filter(highest=True).update(highest=False)
            Bids.objects.create(bid=new_bid, bid_user=request.user, auction=auction, highest=True)
        else:
            return auction_view(request, auction_id, msg="Your bid has to be higher than the current bid.")
    return auction_view(request, auction_id)

def close_auction(request):
    auction_id = int(request.GET['auctionId'])
    Auction_Listing.objects.filter(pk=auction_id).update(closed=True)
    return auction_view(request, auction_id)

def comment_auction(request, auction_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        content = request.POST["comment"]
        auction = util.get_auction(auction_id)
        Comments.objects.create(auction=auction, author=request.user, content=content)
    return auction_view(request, auction_id)

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })

def category_view(request, category_id):
    try:
        category = Categories.objects.get(pk=category_id)
    except KeyError:
        return HttpResponseBadRequest("Bad Request: category is not available")
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Bad Request: category does not exist")
    return render(request, "auctions/category.html", {
        "auctions": category.auctions.filter(closed=False),
        "category": category
    })