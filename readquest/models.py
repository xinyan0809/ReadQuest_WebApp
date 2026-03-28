from django.db import models
from django.template.defaultfilters import slugify
# User model
from django.contrib.auth.models import User
from django.utils import timezone


# User model
class Userpage(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.owner.get_username()

# For our badges 
class Achievement(models.Model):
    MAX_NAME_LENGTH = 128

    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    icon = models.ImageField(blank=True) # TODO Set upload_to= directionary
    earners = models.ManyToManyField(User)

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['earners'])
        super(Achievement, self).save(*args, **kwargs) 
        

    def __str__(self):
        return self.name

# Book details 
class Book(models.Model):
    MAX_TITLE_LENGTH = 128
    MAX_AUTHOR_LENGTH = 128

    isbn = models.IntegerField(unique=True, null=True, blank=True)
    ol_key = models.CharField(max_length=64, unique=True, null=True, blank=True)
    title = models.CharField(max_length=MAX_TITLE_LENGTH)
    author = models.CharField(max_length=MAX_AUTHOR_LENGTH)
    pages = models.IntegerField(default=0)
    cover_image = models.ImageField(null=True, blank=True)
    cover_url = models.URLField(null=True, blank=True)
    wishlisted_by = models.ManyToManyField(User, related_name='wishlisted_by')
    read_by = models.ManyToManyField(User, through='ReadRecord', related_name='read_by')     # so users can see other users on home page
    currently_reading = models.ManyToManyField(User, related_name='currently_reading')

    def save(self, *args,**kwargs):
            self.full_clean(exclude=['cover_image', 'cover_url'])
            self.validate_unique(exclude=['wishlisted_by', 'read_by', 'currently_reading'])
            super(Book ,self).save(*args, **kwargs) 
    
    def __str__(self):
        return self.title

# Tracking book progress of reading
class ProgressRecord(models.Model):
    MAX_NAME_LENGTH = 128

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=MAX_NAME_LENGTH, unique=True)
    stage_final = models.IntegerField()
    stage_current = models.IntegerField()
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ProgressRecord, self).save(*args, **kwargs) 

    def __str__(self):
        return self.name

# Tracking user records for goals and lists
class ReadRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    # So we can track goals
    date_read = models.DateTimeField(null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)

# Storing a review for a book
class Review(models.Model):
    text = models.TextField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    def __str__(self):
        return f"Review of book {self.book}"

# Storing a goal
class Goal(models.Model):

    title_goal = models.CharField(max_length=200, default=0)
    books = models.IntegerField(default=0)
    current_goals = models.ManyToManyField(User, related_name='current_goals')
    completed_by = models.ManyToManyField(User, related_name='completed_goals', blank=True)

    # Track time on goals
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['current_goals', 'completed_by'])
        super(Goal, self).save(*args, **kwargs) 


