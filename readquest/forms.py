from django import forms
from django.contrib.auth.models import User
from .models import Review
from .models import Book
from .models import Goal

# For login
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

# Adding a review
class ReviewForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(),
                           help_text="Leave a review...")

    class Meta:
        model = Review
        exclude = ('book',)
        fields = ('text',)

# For adding a each book
class BookForm(forms.ModelForm):
    isbn = forms.IntegerField(help_text="Enter ISBN of book (optional)", required=False)
    title = forms.CharField(max_length=Book.MAX_TITLE_LENGTH,
                            help_text="Book Title")
    author = forms.CharField(max_length=Book.MAX_AUTHOR_LENGTH,
                            help_text="Author Name")
    pages = forms.IntegerField(min_value=1)
    blurb = forms.CharField(widget=forms.HiddenInput(), 
                            initial="This is a user submitted book.")
    cover_image = forms.ImageField(required=False)


    class Meta:
        model = Book
        fields = ('isbn', 'title', 'author', 'pages', 'blurb', 'cover_image',)

# Adding a goal
class GoalForm(forms.ModelForm):
    title_goal = forms.CharField(help_text="Your goal title", required=True)
    books = forms.IntegerField(help_text="Enter the amount of books you want to read", required=True)

    class Meta:
        model = Goal
        fields = ('title_goal', 'books',)


