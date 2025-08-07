from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing


def index(request):
    active_listings = Listing.objects.filter(isActive=True)
    all_categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
        "categories": all_categories
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
    

def createListing(request):
    if request.method == "GET":
        # generate create_listing page
        all_categories = Category.objects.all()
        return render(request, "auctions/create.html", {
            "categories": all_categories
        })
    else:
        # fetch user listing data
        title = request.POST["title"]
        description = request.POST["description"]
        image = request.POST["image-url"]
        price = request.POST["price"]
        category = Category.objects.get(
            categoryName = request.POST["category"]
        )
        curr_user = request.user

        user_listing = Listing(
            title = title,
            description = description,
            imageURL =  image,
            price = float(price),
            owner = curr_user,
            category = category
        )
        user_listing.save()
        return HttpResponseRedirect(reverse("index"))


def show_category(request):
    if request.method == "POST":
        category = request.POST.get('category')
        return redirect("show_category_detail", name=category)
    

def show_category_detail(request, name):
    selected_category = Category.objects.get(
        categoryName = name
    )
    active_listings = Listing.objects.filter(category = selected_category)
    all_categories = Category.objects.all()
    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
        "categories": all_categories
    })

def show_listing(request, id):
    listing = Listing.objects.get(pk=id)
    inUserWatchlist = request.user in listing.watchlist.all()
    #try: inUserWatchlist
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "inUserWatchlist": inUserWatchlist
    })

def removeFromWatchlist(request, id):
    listing = Listing.objects.get(pk=id)
    user = request.user
    listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse("show_listing", args=(id, )))


def addToWatchlist(request, id):
    listing = Listing.objects.get(pk=id)
    user = request.user
    listing.watchlist.add(user)
    return HttpResponseRedirect(reverse("show_listing", args=(id, )))