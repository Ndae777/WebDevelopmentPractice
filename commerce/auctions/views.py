from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Auction_listing, Bid, Comment , WatchList
from django.contrib.auth.decorators import login_required

class CreateListing(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.IntegerField()
    image_url = forms.URLField(required=False) #making it optional 
    category = forms.CharField(max_length=64)
    active = forms.BooleanField(required=False) #helps for form to start as false

def index(request):
    auction_listing = Auction_listing.objects.all() #auction listing table 
    return render(request, "auctions/index.html", {
        "Auction_listings" : auction_listing, 
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


def create_listing(request):

    if request.method == "POST":
        form = CreateListing(request.POST)
        if form.is_valid():
           auction_listing = Auction_listing(
                item_name = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                start_bid = form.cleaned_data["starting_bid"],
                owner = request.user , 
                image_url = form.cleaned_data["image_url"],
                category = form.cleaned_data["category"],
                active = form.cleaned_data["active"]
            )
           
           auction_listing.save()
           return HttpResponseRedirect(reverse("index"))
    
    return render(request, "auctions/create_listing.html", {
        "form" : CreateListing(),
    })
    
@login_required
def listing_page(request, listing_id):

    auction_listing = Auction_listing.objects.get(id=listing_id)

    
    watchlist_present = WatchList.objects.filter(
        watchlist_owner = request.user, 
        item = auction_listing
        ).exists() # returns true if the item and owner already in watchlist else false
    
    response_message  = "Nothing" #  message to display for user feedback. 
    close_ownership = False  # bool to see if there's ownership to closing bid
    #close logic
    if request.user == auction_listing.owner:
        close_ownership = True
    
    elif request.method == "POST":
        if "watchlist_act" in request.POST:
            if request.POST["watchlist_act"] == "Add to WatchList":
                watchlist_to_save = WatchList(
                    watchlist_owner = request.user,
                    item = auction_listing,
                )

                watchlist_to_save.save()
                return HttpResponseRedirect(reverse('index'))

            elif request.POST["watchlist_act"] == "Remove from WatchList":
                watchlist_to_delete = WatchList.objects.get(
                    watchlist_owner= request.user,
                    item= auction_listing,
                )

                watchlist_to_delete.delete()
                return HttpResponseRedirect(reverse('index'))           
            
        if "Bid_submit" in request.POST:

        #dealing with bid logic 
            bid_amount = int(request.POST["bid"]) #fixed to convert it into a integer
            highest_bid = auction_listing.start_bid 
            bids_on_the_item = Bid.objects.filter(item=auction_listing)

            for all_bids in bids_on_the_item:
                if all_bids.bid_amount > highest_bid :
                    highest_bid = all_bids.bid_amount #highest bid saved here

            if bid_amount > highest_bid:
                bid_saving = Bid(
                    bidder = request.user,
                    item = auction_listing,
                    bid_amount = bid_amount,
                )

                bid_saving.save()
                response_message = "Bid Successful."
            else:
                response_message  = f"Bid Unsuccessful, Bid a higher amount than ${highest_bid}. Current Bid too low"
        
        # dealing with close bid logic
        if "Close_bid" in request.POST:

            auction_listing.active = False
            auction_listing.save()

            bid_on_item = Bid.objects.filter(item = auction_listing)
            highest_bid = None
            highest_bid_amount = auction_listing.start_bid

            for bids in bid_on_item:
                if bids.bid_amount > highest_bid_amount:
                    highest_bid_amount = bids.bid_amount
                    highest_bid = bids

            if highest_bid is not None:
                auction_listing.winner = highest_bid.bidder
        
    
    return render(request, "auctions/listing_page.html", {
        "auction_listing" : auction_listing,
        "listing_id" : listing_id,
        "watchlist_present" : watchlist_present,
        "success_message" : response_message,
        "close_ownership": close_ownership
    })
