from django.db import models

# Create your models here.
from django.contrib.auth.models import User

User._meta.get_field('email')._unique = True
