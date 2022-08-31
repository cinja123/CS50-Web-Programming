from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone


class User(AbstractUser):
    pass

class Categories(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return self.category


class Auction_Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(max_digits=10, decimal_places=2, validators = [MinValueValidator(0.0)])
    image_url = models.URLField(max_length=200, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    categories = models.ManyToManyField(Categories, related_name="auctions", blank=True)
    date_published = models.DateTimeField(default=timezone.now)
    closed = models.BooleanField()

    def __str__(self):
        return f"{self.title} by {self.creator}"

    def get_current_price(self):
        bids = self.bids.filter(highest=True)
        if len(bids) == 0:
            return float(self.start_bid)
        elif len(bids) == 1:
            return float(bids[0].bid)
        else:
            return -1

class Bids(models.Model):
    bid = models.DecimalField(max_digits=10, decimal_places=2, validators = [MinValueValidator(0.0)])
    bid_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="all_bids")
    auction = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name="bids")
    highest = models.BooleanField()

    def __str__(self):
        return f"{self.bid_user} bid $ {self.bid} on {self.auction}"


class Comments(models.Model):
    auction = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.author} commented {self.auction} on {self.created}"

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    auction = models.ForeignKey(Auction_Listing, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.user} watches {self.auction}"