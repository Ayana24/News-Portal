from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        posts_rating = self.post_set.aggregate(total_rating=models.Sum('rating'))[
                           'total_rating'] * 3 if self.post_set.exists() else 0

        author_comments_rating = Comment.objects.filter(user=self.user).aggregate(total_rating=models.Sum('rating'))[
            'total_rating'] if Comment.objects.filter(user=self.user).exists() else 0

        post_comments_rating = Comment.objects.filter(post__author=self).aggregate(total_rating=models.Sum('rating'))[
            'total_rating'] if Comment.objects.filter(post__author=self).exists() else 0

        self.rating = (posts_rating or 0) + (author_comments_rating or 0) + (post_comments_rating or 0)
        self.save()


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    ARTICLE = 'AR'
    NEWS = 'NW'
    POST_TYPES = [
        (ARTICLE, 'Статья'),
        (NEWS, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=2, choices=POST_TYPES, default=ARTICLE)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...' if len(self.text) > 124 else self.text

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return f'Комментарий от {self.user.username} к {self.post.title}'

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
