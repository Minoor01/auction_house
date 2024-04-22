from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from django.contrib import admin
from django.core.mail import send_mail

class AuctionItem(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    start_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(blank=True, null=True)
    end_time = models.DateTimeField(blank=True, null=True)
    image = models.ImageField(upload_to='auction_item_images/', blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='won_auctions')
    sketchfab_script = models.TextField(blank=True, null=True)  # New field for Sketchfab script

    APPROVAL_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    approval_status = models.CharField(max_length=10, choices=APPROVAL_CHOICES, default='pending')


    def is_live(self):
        return self.start_time <= timezone.now() <= self.end_time

    def is_upcoming(self):
        return self.start_time > timezone.now()

    def is_past(self):
        return self.end_time is not None and self.end_time < timezone.now()

    def determine_winner(self):
        highest_bid = self.bid_set.order_by('-amount').first()
        if highest_bid:
            self.winner = highest_bid.bidder
            self.save()
            # if self.winner.email:
            #     subject = 'Congratulations! You won the auction'
            #     message = render_to_string('winner_email.html', {'auction_item': self})
            #     send_mail(subject, message, 'your_email@example.com', [self.winner.email])
        
            return self.winner
        else:
            self.winner = None
            self.save()
            return None

    def get_winner_details(self):
        if self.winner:
            return f"Winner: {self.winner.username}, Winning Bid: {self.current_bid}"
        else:
            return "No winner yet"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(AuctionItem, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.bidder.username} on {self.item.title} for {self.amount}"

class AuctionItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'start_time', 'end_time', 'approval_status']
    list_filter = ['approval_status']
    search_fields = ['title', 'created_by__username']

    def save_model(self, request, obj, form, change):
        if change:
            orig_obj = AuctionItem.objects.get(pk=obj.pk)
            if orig_obj.approval_status == 'pending' and obj.approval_status == 'approved':
                subject = f'Your auction item "{obj.title}" has been approved'
                message = f'Your auction item "{obj.title}" has been approved and is now listed.'
                # send_mail(subject, message, '#change this', [obj.created_by.email])
        obj.save()

class RefundRequest(models.Model):
    reason = models.TextField()
    bank_branch = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reason  # Display reason as the string representation of the object