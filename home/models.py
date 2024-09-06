from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# User model with additional fields for the dashboard
class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    dob = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=50)
    email_verified = models.BooleanField(default=False)
    phone = models.CharField(max_length=13)
    password = models.CharField(max_length=12, default='sohaib123')
    reputation = models.IntegerField(default=0)  # For user reputation

    def __str__(self):
        return self.username

    @property
    def total_posts(self):
        return self.post_data_set.count()  # Count total posts by the user

    @property
    def total_likes_given(self):
        return self.like_set.count()  # Count total likes given by the user

    @property
    def total_likes_received(self):
        return sum(post.total_likes for post in self.post_data_set.all())  # Count total likes received on user's posts

    @property
    def total_comments(self):
        return self.comment_set.count()  # Count total comments made by the user
    
    @property
    def total_matches(self):
        return self.match_user_set.count()


# Skill offer model for the dashboard
class Skilloffer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill_offered = models.CharField(max_length=255)
    experience_level_offered = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.user.username}: {self.skill_offered}"


# Skills needed model for the dashboard
class SkillsNeeded(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=50)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.user.username}: {self.skill}"


# Post data model to track posts made by users
class Post_data(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mypost = models.TextField()
    time_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.mypost[:20]  # Return first 20 characters of the post

    @property
    def total_likes(self):
        return self.like_set.count()  # Total likes for a post

    @property
    def total_comments(self):
        return self.comment_set.count()  # Total comments on a post


# Like model to track likes on posts
class Like(models.Model):
    post = models.ForeignKey(Post_data, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} liked {self.post.mypost[:20]}"


# Comment model to track comments on posts
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post_data, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.comment[:20]  # Return first 20 characters of the comment


# CommentLike model to track likes on comments
class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.username} liked {self.comment.comment[:20]}"


class SwapHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='swap_histories')
    skill_offered = models.CharField(max_length=255)
    skill_needed = models.CharField(max_length=255)
    swap_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[
        ('completed', 'Completed'),
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
    ], default='pending')

    def __str__(self):
        return f"Swap by {self.user.username} on {self.swap_date}"

    class Meta:
        verbose_name = 'Swap History'
        verbose_name_plural = 'Swap Histories'
        ordering = ['-swap_date']

class MatchSuggestion(models.Model):
    user = models.ForeignKey(User, related_name='match_suggestions', on_delete=models.CASCADE)
    match_user = models.ForeignKey(User, related_name='matches', on_delete=models.CASCADE)
    match_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Example field for score or relevance
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'match_user')  # Ensures no duplicate matches

    def __str__(self):
        return f'{self.user.username} matched with {self.match_user.username}'