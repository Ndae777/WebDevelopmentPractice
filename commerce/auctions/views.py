from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Auction_listing, Bid, Comment


def index(request):
    return render(request, "auctions/index.html")


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

class CreateListing(forms.Form):
    title = forms.CharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea)
    starting_bid = forms.IntegerField()
    image_url = forms.URLField(required=False) #making it optional 
    category = forms.CharField(max_length=64)
    active = forms.BooleanField(required=False) #helps for form to start as false

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