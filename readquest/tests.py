from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import *

class ModelTests(TestCase):

    def setUp(self):
        # Create a user for testing
        self.long_string = '.'* 999
        self.user = User.objects.create(username='bobert', password='coolestpassworf')

    def test_userpage_creation(self):
        userpage = Userpage.objects.create(owner=self.user)
        self.assertEqual(self.user, userpage.owner)

    def test_achievement_creation(self):
        achievement = Achievement.objects.create(name="Speed Reader")
        achievement.earners.add(self.user)
        self.assertEqual(achievement.name, "Speed Reader")
        self.assertIn(self.user, achievement.earners.all())

    def test_book_creation(self):
        book = Book.objects.create(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            pages=180,
            ol_key="1234567"
        )
        book.wishlisted_by.add(self.user)
        self.assertEqual(book.title, "The Great Gatsby")
        self.assertIn(self.user, book.wishlisted_by.all())

    def test_progress_record_creation(self):
        book = Book.objects.create(title="Loreum Ipsum", author="Steve Jobs")
        progress = ProgressRecord.objects.create(
            owner=self.user,
            name="How to be Me",
            stage_final=180,
            stage_current=50,
            book=book
        )
        self.assertEqual(progress.name, "How to be Me")
        self.assertEqual(progress.book.title, "Loreum Ipsum")

    # 5. ReadRecord Tests
    def test_read_record_creation(self):
        date = datetime(2026, 9, 12, 21, 30)
        book = Book.objects.create(title="Harry Potter and the Great Pile of Ash", author="JK!")
        read_record = ReadRecord.objects.create(
            user=self.user,
            book=book,
            rating=5,
            date_read=date
        )
        self.assertEqual(read_record.rating, 5)
        self.assertEqual(read_record.user, self.user)
        self.assertEqual(read_record.date_read, date)
        self.assertEqual(book.title, "Harry Potter and the Great Pile of Ash")

    def test_review_creation(self):
        book = Book.objects.create(title="Cooking 301", author="Oranje Djuss")
        review = Review.objects.create(text="Burnt my house down.", book=book)
        self.assertEqual(str(review), f"Review of book {book.title}")
        self.assertEqual(book, review.book)

    def test_goal_creation(self):
        goal = Goal.objects.create(title_goal="4 in 10 Challenge", books=10)
        goal.current_goals.add(self.user)
        self.assertEqual(goal.title_goal, "4 in 10 Challenge")
        self.assertIn(self.user, goal.current_goals.all())

    def test_achievement_max(self):
        
        test_icon = SimpleUploadedFile("stuff.jpg", b"blblbl", content_type="image/jpg")
        achievement = Achievement(name=self.long_string, icon=test_icon)
        
        with self.assertRaises(ValidationError):
            achievement.save()
        
    def test_book_max(self):
        book = Book(title=self.long_string, author='Mr. Nil')
        with self.assertRaises(ValidationError):
            book.save()
        book2 = Book(title='Johnny Boy', author=self.long_string)
        with self.assertRaises(ValidationError):
            book.save()

    def test_progress_max(self):
        progress = ProgressRecord(owner=self.user, name=self.long_string, stage_final=20, stage_current=0)

        with self.assertRaises(ValidationError):
            progress.save()

    def test_goal_max(self):
        goal = Goal(title_goal=self.long_string)

        with self.assertRaises(ValidationError):
            goal.save()
        



class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='bobert', password='coolestpassword')
        self.client = Client()

    def test_home_forbidden(self):
        response = self.client.get(reverse('readquest:home'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/readquest/login/?next=/readquest/home/')

    def test_profile_forbidden(self):
        response = self.client.get(reverse('readquest:profile'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/readquest/login/?next=/readquest/profile/')
    
    def test_catalogue_forbidden(self):
        response = self.client.get(reverse('readquest:catalogue_book-search'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/readquest/login/?next=/readquest/catalogue/')
        
    
    def test_login_not_forbidden(self):
        response = self.client.get(reverse('readquest:index'))
        self.assertEqual(response.status_code, 200)

    def test_register_not_forbidden(self):
        response = self.client.get(reverse('readquest:register'))
        self.assertEqual(response.status_code, 200)

    def test_valid_register(self):
        response = self.client.post(reverse('readquest:register'), {
            'username' : 'billybob',
            'password' : 'stephaen',
            'confirm_password' : 'stephaen'
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('readquest:index'))
        self.assertTrue(User.objects.filter(username='billybob').exists())

    def test_password_dont_match(self):
        response = self.client.post(reverse('readquest:register'), {
            'username' : 'billybob',
            'password' : 'stephaen',
            'confirm_password' : 'seven'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Passwords do not match')
    
    def test_password_too_short(self):
        response = self.client.post(reverse('readquest:register'), {
            'username' : 'billybob',
            'password' : 'steven',
            'confirm_password' : 'seven'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Password must be at least 8 characters long.')

    def test_valid_login(self):
        user = User.objects.create_user(
            username='billybob',
            password='stephaen'
        )
        response = self.client.post(reverse('readquest:home'), {
            'username' : 'billybob',
            'password' : 'stephaen',
            'remember_me' : 'off',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/readquest/login/?next=/readquest/home/')

    def test_remember_me(self):
        user = User.objects.create_user(
            username='billybob',
            password='stephaen'
        )
        response = self.client.post(reverse('readquest:home'), {
            'username' : 'billybob',
            'password' : 'stephaen',
            'remember_me' : 'on',
        })

        self.assertEqual(self.client.session.get_expiry_age(), 1209600)

class LoggedInTests(TestCase):
    def setUp(self):
        self.user = self.user = User.objects.create(username='bobert', password='coolestpassword')
        self.client.force_login(self.user)
        self.book1 = Book.objects.create(title="Cooking 301", author="Oranje Djuss")
        self.book2 = Book.objects.create(title="Harry Potter and the Great Pile of Ash", author="JK!")
        self.book3 = Book.objects.create(title="Loreum Ipsum", author="Steve Jobs")

        ReadRecord.objects.create(user=self.user, book=self.book1)
        self.book2.wishlisted_by.set([self.user])
        self.book3.currently_reading.set([self.user])

    def test_profile_dict(self):
        response = self.client.get(reverse('readquest:profile'))
        read_books = response.context['read_books']
        wishlisted = response.context['wishlisted']
        currently_reading = response.context['current_read']

        self.assertTrue(read_books.filter(book=self.book1).exists())
        self.assertIn(self.book2, response.context['wishlisted'])
        self.assertIn(self.book3, response.context['current_read'])

    


    
        

