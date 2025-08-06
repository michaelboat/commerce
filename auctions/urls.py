from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("/login", views.login_view, name="login"),
    path("/logout", views.logout_view, name="logout"),
    path("/register", views.register, name="register"),
    path("/create", views.createListing, name="create"),
    path("/category", views.show_category, name="show_category"),
    path("/category/<slug:name>", views.show_category_detail, name="show_category_detail"),
    path("/listings/<int:id>", views.show_listing, name="show_listing")
]
