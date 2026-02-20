from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Auction_listings(models.Model):
    pass

class Bids(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    bid_amount = models.IntegerField()

    def __str__(self):
        return f"Bid {self.id} from {self.bidder_id.username} is ${self.bid_amount}"

class Comments(models.Model):
    commentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="commentor")
    comment = models.TextField()

    def __str__(self):
        return f"Comment {self.id} from {self.commentor.username} is : {self.comment}"