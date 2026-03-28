from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse
from readquest.forms import UserForm, BookForm, GoalForm
from .models import Book, Goal, ProgressRecord, Achievement, ReadRecord

from .services import search_books

# Being able to track the goals from when a new goal is set up
from django.utils import timezone


# Create your views here.

def land_register(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # 1. check the passwords match
        if password != confirm_password:
            print("Error: Passwords do not match")
            return render(request, 'readquest/register.html', {'error': 'Passwords do not match. Please try again.'})

        # 2. check the password length
        if len(password) < 8:
            print("Error: Password too short")
            return render(request, 'readquest/register.html', {'error': 'Password must be at least 8 characters long.'})

        # 3. check the password complexity (at least one uppercase letter, one lowercase letter, and one digit)
        if user_form.is_valid():
            user = user_form.save(commit=False)

            user.set_password(user.password)

            user.save()

            return redirect(reverse('readquest:index'))
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()

    return render(request, 'readquest/register.html', {'user_form': user_form})

def user_login(request):
    EXPIRY_TIME = 1209600   # 2 weeks in seconds
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        username = request.POST['username']
        password = request.POST['password']
        remember_me = request.POST.get('remember_me')
        
        if form.is_valid():
            user = form.get_user()
            if user.is_active:
                login(request, user)
                if remember_me:
                    request.session.set_expiry(EXPIRY_TIME)
                else:
                    request.session.set_expiry(0)  # expires when browser closes
                return redirect(reverse('readquest:home'))
            else:
                messages.error(request, "Your ReadQuest account is disabled.")
                return redirect(reverse('readquest:index'))
        else:
            messages.error(request, "Invalid username or password.")
            return redirect(reverse('readquest:index'))
    else:
        form = AuthenticationForm()

        return render(request, 'readquest/index.html', {'form': form})

@login_required
def user_logout(request):
    
    logout(request)

    # Take the user back to the un-authroised home 
    return redirect(reverse('readquest:index'))

def index(request):

    return render(request,'readquest/index.html')

@login_required
def home(request):
    context_dict = {}
    context_dict['user'] = request.user #fetches the user that sent the request
    context_dict['achivements'] = Achievement.objects.filter(earners=request.user)
    context_dict['current_read'] = Book.objects.filter(currently_reading=request.user)
    context_dict['goals'] = current_goals(request.user)
    context_dict['progress_records'] = current_book_progress(request.user)

    # for users to be able to see other users
    context_dict['user_activity'] = ReadRecord.objects.exclude(user=request.user).select_related('user', 'book',).order_by('-date_read')[:10]

    return render(request, 'readquest/home.html', context=context_dict)

# The books that a user has read and had on their wishlist
@login_required
def book_list(request):
    context_dict = {}
    context_dict['read_books'] = ReadRecord.objects.filter(user=request.user).select_related('book')
    context_dict['wishlisted'] = Book.objects.filter(wishlisted_by=request.user)
    return render(request, 'readquest/home.html', context=context_dict)

@login_required
def profile(request):
    context_dict = {}
    context_dict['read_books'] = ReadRecord.objects.filter(user=request.user).select_related('book')
    context_dict['current_read'] = Book.objects.filter(currently_reading=request.user)
    context_dict['wishlisted'] = Book.objects.filter(wishlisted_by=request.user)
    context_dict['goals'] = current_goals(request.user)
    context_dict['progress_records'] = current_book_progress(request.user)

    # Badges
    context_dict['badges'] = Achievement.objects.filter(earners=request.user)
    context_dict['badge_read_10'] = ReadRecord.objects.filter(user=request.user).count() >= 10
    context_dict['badge_first_goal'] = Goal.objects.filter(completed_by=request.user).exists()
    context_dict['badge_harry_potter'] = ReadRecord.objects.filter(user=request.user, book__title__icontains='Harry Potter').exists()
    context_dict['badge_wishlist'] = Book.objects.filter(wishlisted_by=request.user).count() >= 5

    return render(request, 'readquest/profile.html', context=context_dict)

# When user finishes a book
@login_required
def finish_book(request, book_id):
    if request.method == 'POST':

        # get the book id and remove it from current read
        try:
            book = Book.objects.get(id=book_id)
            book.currently_reading.remove(request.user)

            rating = request.POST.get('rating') #user can add a rating
            try:
                rating = int(rating) if rating else None
                if rating and not (1 <= rating <= 5):
                    rating = None
            except (ValueError, TypeError):
                rating = None

            # log book as finished with the timestamp and rating
            ReadRecord.objects.create(user=request.user, book=book, date_read=timezone.now(), rating=rating)
            _check_and_complete_goals(request.user) #check if finished book completes a goal
        except Book.DoesNotExist:
            pass
    return redirect(reverse('readquest:profile'))

@login_required
def add_to_currently_reading(request):
    if request.method == 'POST':
        # get book details
        ol_key = request.POST.get('ol_key', '').strip()
        title = request.POST.get('title', 'Unknown Title').strip()
        author = request.POST.get('author', 'Unknown Author').strip()
        pages = request.POST.get('pages', 0)
        cover_url = request.POST.get('cover_url', '').strip()

        try:
            pages = int(pages)
        except (ValueError, TypeError):
            pages = 0

        # get book if exists, of not create one
        book, _ = Book.objects.get_or_create(
            ol_key=ol_key,
            defaults={
                'title': title,
                'author': author,
                'pages': pages,
                'cover_url': cover_url or None,
            }
        )
        
        # add to current read or wishlist
        book.currently_reading.add(request.user)
        book.wishlisted_by.remove(request.user)

    return JsonResponse({
        "success" : True,
        "message" : "Book added",
    })

@login_required
def add_to_wishlist(request):
    if request.method == 'POST':
        # get book details
        ol_key = request.POST.get('ol_key', '').strip()
        title = request.POST.get('title', 'Unknown Title').strip()
        author = request.POST.get('author', 'Unknown Author').strip()
        pages = request.POST.get('pages', 0)
        cover_url = request.POST.get('cover_url', '').strip()

        try:
            pages = int(pages)
        except (ValueError, TypeError):
            pages = 0

        # get book if exists, of not create one
        book, _ = Book.objects.get_or_create(
            ol_key=ol_key,
            defaults={
                'title': title,
                'author': author,
                'pages': pages,
                'cover_url': cover_url or None,
            }
        )

        # add to or wishlist
        book.wishlisted_by.add(request.user)


    return JsonResponse({
        "success" : True,
        "message" : "Book added",
    })

@login_required
def goals(request):
    context_dict = {'progress_record': ProgressRecord.objects.filter(owner=request.user)}
    context_dict['goals'] = current_goals(request.user)
    context_dict['completed_goals'] = completed_goals(request.user)

    # Badges
    context_dict['badge_read_10'] = ReadRecord.objects.filter(user=request.user).count() >= 10
    context_dict['badge_first_goal'] = Goal.objects.filter(completed_by=request.user).exists()
    context_dict['badge_harry_potter'] = ReadRecord.objects.filter(user=request.user, book__title__icontains='Harry Potter').exists()
    context_dict['badge_wishlist'] = Book.objects.filter(wishlisted_by=request.user).count() >= 5
    return render(request,'readquest/goals.html', context=context_dict)

def current_goals(user):
    goals = Goal.objects.filter(current_goals=user)

    for goal in goals:
        # only count books after goal the started
        books_read_count = ReadRecord.objects.filter(
            user=user,
            date_read__gte=goal.created_at).count()

        goal.progress = min((books_read_count / goal.books * 100), 100)
        goal.books_read = books_read_count

    return goals

def completed_goals(user):
    goals = Goal.objects.filter(completed_by=user).order_by('-completed_at')

    for goal in goals:
        books_read_count = ReadRecord.objects.filter(
            user=user,
            date_read__gte=goal.created_at,
            date_read__lte=goal.completed_at).count()
        goal.books_read = books_read_count

    return goals

def _check_and_complete_goals(user):
    """After finishing a book, archive any goals that have reached their target."""
    active_goals = Goal.objects.filter(current_goals=user)

    for goal in active_goals:
        books_read_count = ReadRecord.objects.filter(
            user=user,
            date_read__gte=goal.created_at).count()

        if books_read_count >= goal.books:
            goal.current_goals.remove(user)
            goal.completed_by.add(user)
            goal.completed_at = timezone.now()
            goal.save()

def show_details(request, details_slug):
    context_dict = {}

    try:
        details = Details.objects.get(slug=details_slug)
        book = details.objects.select_related('book').get()
        context_dict['details'] = details
        context_dict['book'] = book

    except Detail.DoesNotExist:
        context_dict['details'] = None
        context_dict['book'] = None

    except Book.DoesNotExist:
        context_dict['details'] = None
        context_dict['book'] = None

    return render(request, 'readquest/details.html', context=context_dict)

def book_review(request, details_slug):
    # Display details for book
    try:
        details = Details.objects.get(slug=details_slug)
        book = details.parent

    except Detail.DoesNotExist:
        book = None

    except Book.DoesNotExist:
        book = None

    if book is None:
        return redirect('') # Where to redirect?

    form = ReviewForm()

    # Form submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)

        if form.is_valid():
            if book:
                review = form.save()

            return redirect(reverse('readquest:details',
                                     kwargs={'details_slug':
                                             details_slug}))

    context_dict = {'form': form, 'book': book}
    return render(request, 'readquest/review.html', context=context_dict)

@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        next_url = request.POST.get('next', reverse('readquest:profile'))

        if form.is_valid():
            book = form.save()
            book.currently_reading.add(request.user)
            return redirect(next_url)

        else:
            print(form.errors)

    return redirect(reverse('readquest:profile'))

@login_required
def add_goal(request):
    if request.method == 'POST':
        form = GoalForm(request.POST, request.FILES)
        next_url = request.POST.get('next', reverse('readquest:profile'))

        if form.is_valid():
            goal = form.save()
            goal.current_goals.add(request.user)
            return redirect(next_url)

        else:
            print(form.errors)

    return redirect(reverse('readquest:profile'))

@login_required
def catalogue(request):
    query = request.GET.get("q", "").strip()
    results = []
    
    # results from search
    if query:
        try: 
            results = search_books(query)

            user_books_in_reading = set(request.user.currently_reading.values_list('ol_key', flat=True))
            user_books_in_wishlist = set(request.user.wishlisted_by.values_list('ol_key', flat=True))
            
            for book in results:
                book['is_in_reading'] = book['ol_key'] in user_books_in_reading
                book['is_in_wishlist'] = book['ol_key'] in user_books_in_wishlist

        except Exception as e:
            messages.error(request, "Please try again")
    return render(request, "readquest/catalogue_book-search.html", {"results": results, "query": query})

@login_required
def update_progress(request, book_id):

    # get number of pages read on that book 
    if request.method == 'POST':
        pages_read = int(request.POST.get('pages_read', 0))
        book = Book.objects.get(id=book_id)
        next_url = request.POST.get('next', reverse('readquest:profile'))

        # check current progress and update the current page 
        try:
            progress = ProgressRecord.objects.get(owner=request.user, book=book)
            progress.stage_current = pages_read
            progress.save()
            return redirect(next_url)

        #  if the progress doesn't exist
        except ProgressRecord.DoesNotExist:
            ProgressRecord.objects.create(
                owner=request.user,
                book=book,
                name=f"{request.user.username}_{book.title}",
                stage_final=book.pages,
                stage_current=pages_read,
            )

    return redirect('readquest:profile')

def current_book_progress(user):
    # get progress for the user
    records = ProgressRecord.objects.filter(owner=user)

    # percentage of book read
    # make sure that 
    for record in records:
        if record.stage_final and record.stage_final > 0:
            record.percent = round((record.stage_current / record.stage_final) * 100)
        else:
            record.percent = 0

    return records
