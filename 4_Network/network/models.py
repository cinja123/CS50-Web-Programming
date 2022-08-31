from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    picture = models.ImageField(upload_to='network/', blank=True)

class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    like = models.ManyToManyField(User, blank=True, related_name="like_users")

    def __str__(self):
        return f"Post {self.id} from {self.creator} on {self.timestamp}"


class Follower(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following_user")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")

    def is_valid_follower(self):
        return self.following != self.follower

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"







