from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import User, Category, Listing, Comment, Bid


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
        # get min_bid price
        price = request.POST["price"]

        category = Category.objects.get(
            categoryName = request.POST["category"]
        )
        curr_user = request.user
        bid = Bid(bid=float(price), user=curr_user)

        user_listing = Listing(
            title = title,
            description = description,
            imageURL =  image,
            price = bid,
            owner = curr_user,
            category = category
        )
        bid.save()
        user_listing.save()

        return HttpResponseRedirect(reverse("index"))


def show_category(request):
    if request.method == "POST":
        category = request.POST.get('category')
        return redirect("show_category_detail", name=category)
    

def show_category_detail(request, name):
    if name == "All":
        return HttpResponseRedirect(reverse("index"))
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
    comments = Comment.objects.filter(listing=listing)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "inUserWatchlist": inUserWatchlist,
        "comments": comments
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


def viewWatchlist(request):
    user = request.user
    listings = user.userWatchlist.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings
    })


def addComment(request, id):
    user = request.user
    curr_listing = Listing.objects.get(pk=id)
    message = request.POST["comment"]
    comment = Comment(
        author = user,
        listing = curr_listing,
        message = message
    )
    comment.save()
    return HttpResponseRedirect(reverse("show_listing", args=(id, )))


def add_bid(request, id):
    user = request.user
    curr_listing = Listing.objects.get(pk=id)
    user_bid_price = request.POST["user_bid"]
    if user_bid_price >  curr_listing.price.bid:
        new_bid = Bid(
            bid = user_bid_price,
            user = user )
        new_bid.save()
        curr_listing.price = new_bid
        curr_listing.save()
        return HttpResponseRedirect(reverse("show_listing", args=(id, ), kwargs="Bid placed succesfully"))
    else:
        return HttpResponseRedirect(reverse("show_listing", args=(id, ), kwargs=f"Bid must be minimum {curr_listing.price.bid}"))
