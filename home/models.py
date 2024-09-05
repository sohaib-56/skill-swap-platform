from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=50,unique=True)
    dob = models.DateField(null=True,blank=True)
    email = models.EmailField(max_length=50)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=13)
    password = models.CharField(max_length=12,default='sohaib123')
    reputation = models.IntegerField(default=0)

    def __str__(self) :
        return self.first_name
    
class Skilloffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_offered = models.CharField(max_length=255)
    experience_level_offered = models.CharField(max_length=50)

    def __str__(self):
        return self.skill_offered


class SkillsNeeded(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=50)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return self.skill

class Post_data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mypost = models.TextField()
    time_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.mypost

    @property
    def total_likes(self):
        return self.like_set.count()


class Like(models.Model):
    post = models.ForeignKey(Post_data, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f'{self.user.username} liked {self.post.mypost[:20]}'
    
class Comment(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    post = models.ForeignKey(Post_data, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment
    
class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f'{self.user.username} liked {self.comment.comment[:20]}'