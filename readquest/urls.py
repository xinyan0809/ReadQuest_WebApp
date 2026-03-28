from django.urls import path
from readquest import views


app_name = 'readquest'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.land_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('profile/', views.profile, name="profile"),
    path('goals/', views.goals, name="goals"),
    path('catalogue/', views.catalogue, name="catalogue_book-search"),
    path('<slug:details_slug>/details', views.show_details, name='details'),
    path('<slug:details_slug>/review', views.book_review, name='review'),
    path('add-to-reading', views.add_to_currently_reading, name="add-to-reading"),
    path('add-to-wishlist', views.add_to_wishlist, name="add-to-wishlist"),
    path('add-book', views.add_book, name="add-book"),
    path('add-goal', views.add_goal, name="add-goal"),
    path('finish-book/<int:book_id>', views.finish_book, name="finish-book"),
    path('book/<int:book_id>/update-progress/', views.update_progress, name="update-progress"),
]

