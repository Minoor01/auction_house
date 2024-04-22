from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator
from website.models import AuctionItem
from django.db.models import Avg

class Buyer_Seller(models.Model):
    user=models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    phone=models.CharField(max_length=11)
    address=models.CharField(max_length=100)
    ratings_sum = models.IntegerField(default=0)
    ratings_count = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def average_rating(self):
        ratings = Rating.objects.filter(buyer_seller=self)
        avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
        return avg_rating if avg_rating else 0

class Rating(models.Model):
    buyer_seller = models.ForeignKey(Buyer_Seller, on_delete=models.CASCADE)
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('buyer_seller', 'item')  # Ensures one review per buyer per item

    def __str__(self):
        return f"{self.buyer_seller.user.username}'s rating for item {self.item}: {self.rating}"