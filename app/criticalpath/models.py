
from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.forms import FileField

from marketplace.models import Transaction, Currency
from .extra import ContentTypeRestrictedFileField
from django_quill.fields import QuillField

from django.core.exceptions import ValidationError

def file_size(value): # add this to some file where you can import it from
    limit = 5 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 5 MB.')


class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class Journey(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(2, "Title must be greater than 2 characters")])
    description = models.TextField(
        validators=[MinLengthValidator(3, "Journey description must be greater than 3 characters")],
        max_length=500, blank=True, null=True
    )
    objective = models.TextField()
    cover_image = models.ImageField(default='static/assets/img/seo-card-image.png', upload_to='journey/cover_images/%Y/%m/%D/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    price = models.PositiveIntegerField(default=10)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='journey_owned')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title




# class Phase(models.Model):
#     title = models.CharField(max_length=200, validators=[MinLengthValidator(2, "Title must be greater than 2 characters")])
#     description = models.TextField()
#     journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
#     phase_number = models.PositiveSmallIntegerField()

#     def __str__(self):
#         return "Phase " + str(self.phase_number)

class Ebook(models.Model):
    NOT_PUBLISHED = 0
    PUBLISHED = 1
    ARCHIVED = 2
    STATUS = [
    (NOT_PUBLISHED, 'Not Published'),
    (PUBLISHED, 'Published'),
    (ARCHIVED, 'Archived'),
    ]
    status = models.IntegerField(choices=STATUS, default=0)
    title = models.CharField(
        validators=[MinLengthValidator(3, "Ebook title must be greater than 3 characters")],
        max_length=50
    )
    excerpt = models.CharField(
        validators=[MinLengthValidator(3, "Ebook excerpt must be greater than 3 characters")],
        max_length=500, blank=True, null=True
    )
    file = models.FileField(upload_to='ebooks/files/', null=True, blank=True, validators=[file_size])
    content = QuillField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    cover_image = models.ImageField(default='seo-card-image.png', upload_to='ebooks/cover_images/', blank=True, null=True)
    price = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(100000)])
    currency_type = models.ForeignKey(Currency, default=1, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title
    

class EbookPaymentSplits(models.Model):
    ebook = models.ForeignKey(Ebook, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()



class Workshop(models.Model):
    NOT_PUBLISHED = 0
    PUBLISHED = 1
    ARCHIVED = 2
    STATUS = [
    (NOT_PUBLISHED, 'Not Published'),
    (PUBLISHED, 'Published'),
    (ARCHIVED, 'Archived'),
    ]
    status = models.IntegerField(choices=STATUS, default=0)
    title = models.CharField(
        validators=[MinLengthValidator(3, "Workshop title must be greater than 3 characters")],
        max_length=50
    )
    excerpt = models.CharField(
        validators=[MinLengthValidator(3, "Workshop excerpt must be greater than 3 characters")],
        max_length=500, blank=True, null=True
    )
    content = QuillField(blank=True, null=True)
    cover_image = models.ImageField(default='seo-card-image.png', upload_to='workshops/cover_images/', blank=True, null=True)
    price = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(100000)])
    currency_type = models.ForeignKey(Currency, default=1, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title

class WorkshopPaymentSplits(models.Model):
    workshop = models.ForeignKey(Workshop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()


class Resource(models.Model):
    NOT_PUBLISHED = 0
    PUBLISHED = 1
    ARCHIVED = 2
    STATUS = [
    (NOT_PUBLISHED, 'Not Published'),
    (PUBLISHED, 'Published'),
    (ARCHIVED, 'Archived'),
    ]
    status = models.IntegerField(choices=STATUS, default=0)
    title = models.CharField(
        validators=[MinLengthValidator(3, "Resource name must be greater than 3 characters")],
        max_length=50
    )
    excerpt = models.CharField(
        validators=[MinLengthValidator(3, "Resource excerpt must be greater than 3 characters")],
        max_length=500, blank=True, null=True
    )
    file = models.FileField(upload_to='resource/files/', null=True, blank=True)
    video = models.FileField(upload_to='resource/videos/', null=True, blank=True)
    content = QuillField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    cover_image = models.ImageField(default='seo-card-image.png', upload_to='resource/cover_images/', blank=True, null=True)
    price = models.PositiveIntegerField(default=1000, validators=[MaxValueValidator(100000)])
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.title



class Course(models.Model):
    NOT_PUBLISHED = 0
    PUBLISHED = 1
    ARCHIVED = 2
    STATUS = [
    (NOT_PUBLISHED, 'Not Published'),
    (PUBLISHED, 'Published'),
    (ARCHIVED, 'Archived'),
    ]
    status = models.IntegerField(choices=STATUS, default=0)
    title = models.CharField(max_length=200, validators=[MinLengthValidator(2, "Title must be greater than 2 characters")])
    excerpt = models.CharField(
        validators=[MinLengthValidator(3, "Course excerpt must be greater than 3 characters")],
        max_length=500, blank=True, null=True
    )
    cover_image = models.ImageField(default='seo-card-image.png', upload_to='course/cover_images/', null=True, blank=True)
    # category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    price = models.PositiveIntegerField(default=10000, validators=[MaxValueValidator(100000)])
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_creator')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class CourseResources(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    #this is used to show the learner the correct ordering the educator intended
    order_no = models.IntegerField()

class CoursePaymentSplits(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.IntegerField()

class Reward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, blank=True, null=True)
    transaction = models.ForeignKey("marketplace.Transaction", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)


# change this to items when implementing for real because this will use resources and courses
class JourneyResources(models.Model):
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)

# class ResourceAdditive(models.Model):
#     title = models.CharField(
#         validators=[MinLengthValidator(3, "Resource name must be greater than 3 characters")],
#         max_length=50
#     )
#     description = models.TextField(
#         validators=[MinLengthValidator(3, "Resource description must be greater than 3 characters")],
#         max_length=500, blank=True, null=True
#     )
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     cover_image = models.ImageField(upload_to='resource/cover_images/%Y/%m/%D/', null=True, blank=False)
#     url = models.URLField(max_length=200, help_text="Help other users find the resource by adding its url. For example, Amazon book link or Coursera course link.", null=True, blank=True)
#     file = models.FileField(upload_to='resource/files/%Y/%m/%D/', null=True, blank=False)
#     resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
#     price = models.PositiveIntegerField(default=10)
#     creator = models.ForeignKey(User, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     last_modified_at = models.DateTimeField(auto_now=True)
#     def __str__(self):
#         return self.title

class CriticalPath(models.Model):
    sequence = models.PositiveIntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, null=True, blank=True)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, null=True, blank=True)
    last_modified_at = models.DateTimeField(auto_now=True)

class Comment(models.Model) :
    comment = models.TextField(
        validators=[MinLengthValidator(3, "Comment must be greater than 3 characters")]
    )
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_at = models.DateTimeField(auto_now=True)

    # Shows up in the admin list
    def __str__(self):
        if len(self.comment) < 15 : return self.comment
        return self.comment[:11] + ' ...'


class Fav(models.Model) :
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # https://docs.djangoproject.com/en/3.0/ref/models/options/#unique-together
    class Meta:
        unique_together = ('journey', 'user')

    def __str__(self) :
        return '%s likes %s'%(self.user.username, self.journey.title[:10])