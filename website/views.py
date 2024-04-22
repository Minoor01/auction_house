# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import AuctionItem, Bid
from .forms import * 
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from userProfile.models import Buyer_Seller, Rating
from django.core.mail import send_mail
from django.template.loader import render_to_string


def live_auction_items(request):
    current_time = timezone.now()
    live_auctions = AuctionItem.objects.filter(approval_status='approved', start_time__lte=current_time, end_time__gt=current_time)
    return render(request, 'live_auction_items.html', {'live_auctions': live_auctions})


def upcoming_auction_items(request):
    current_time = timezone.now()

    upcoming_auctions = AuctionItem.objects.filter(start_time__gt=current_time, end_time__gt=current_time, approval_status='approved')

    return render(request, 'upcoming_auction_items.html', {
        'upcoming_auctions': upcoming_auctions,
    })

def past_auction_items(request=None):
    current_time = timezone.now()

    past_auctions = AuctionItem.objects.filter(start_time__lt=current_time, end_time__lt=current_time, approval_status='approved')

    for auction in past_auctions:
        if not auction.winner:  
            auction.determine_winner() 

    if request:
        return render(request, 'past_auction_items.html', {
            'past_auctions': past_auctions,
        })
        
    else:
        return past_auctions

def auction_detail(request, item_id):
    auction_detail = get_object_or_404(AuctionItem, id=item_id)
    
    if auction_detail.is_past() and not auction_detail.winner:
        auction_detail.determine_winner()
        
    return render(request, 'auction_detail.html', {'auction_detail': auction_detail})


def search_live_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()

    # checks if the query is in the title or address of the auction item
    live_auctions = AuctionItem.objects.filter(
        Q(title__icontains=query) | Q(address__icontains=query),
        end_time__gte=current_time
    )

    return render(request, 'auction_search.html', {'auctions': live_auctions, 'query': query, 'search_type': 'Live Auctions'})

def search_upcoming_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()

    upcoming_auctions = AuctionItem.objects.filter(
        Q(title__icontains=query) | Q(address__icontains=query),
        start_time__gt=current_time,
    )

    return render(request, 'auction_search.html', {'auctions': upcoming_auctions, 'query': query, 'search_type': 'Upcoming Auctions'})


def search_past_auctions(request):
    query = request.GET.get('query', '')
    current_time = timezone.now()

    past_auctions = AuctionItem.objects.filter(
        Q(title__icontains=query) | Q(address__icontains=query),
        end_time__lt=current_time
    )

    return render(request, 'auction_search.html', {'auctions': past_auctions, 'query': query, 'search_type': 'Past Auctions'})


    
@login_required 
def create_auction(request):
    if request.method == 'POST':
        form = AuctionItemForm(request.POST, request.FILES)
        if form.is_valid():
            auction_item = form.save(commit=False)
            auction_item.created_by = request.user
            auction_item.approval_status = 'pending'
            auction_item.save()
            return redirect('website:auction_detail', item_id=auction_item.id)
    else:
        form = AuctionItemForm()

    return render(request, 'create_auction.html', {'form': form})

@login_required
def bidding(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)
    if request.method == "POST":
        form = BiddingForm(request.POST)
        if form.is_valid():
            bid_amount = form.cleaned_data['current_bid']

            # Get the current highest bid for the auction
            highest_bid = Bid.objects.filter(item=auction).order_by('-amount').first()

            if bid_amount >= auction.start_price and (not highest_bid or bid_amount > highest_bid.amount):
                previous_highest_bidder = highest_bid.bidder if highest_bid else None  
                new_bid = Bid.objects.create(bidder=request.user, item=auction, amount=bid_amount)  

                auction.current_bid_by = new_bid.bidder
                auction.current_bid = new_bid.amount
                auction.save()

                if previous_highest_bidder:
                    send_outbid_email(previous_highest_bidder, auction.title, bid_amount)  # Send outbid email

                return redirect('website:live_auction_items')
                
            else:
                message = 'Your bid should be greater than the starting price and the current highest bid.'
                return render(request, 'bidding.html', {'auction': auction, 'form': form, 'message': message})
    else:
        form = BiddingForm()
    return render(request, 'bidding.html', {'auction': auction, 'form': form})

def send_outbid_email(previous_highest_bidder, auction_title, current_highest_bid):
    subject = 'Your bid has been outbid!'
    message = render_to_string('outbid_email.html', {'auction_title': auction_title,'previous_highest_bidder':previous_highest_bidder,'current_highest_bid':current_highest_bid})
    send_mail(subject, message, '#confidential', [previous_highest_bidder.email])


def seller_rating(request, item_id):
    auction = get_object_or_404(AuctionItem, id=item_id)
    buyer_seller = auction.created_by.buyer_seller

    if request.method == "POST":
        rating_value = int(request.POST.get('rating'))

        # Checking if the user has already rated this item
        if not Rating.objects.filter(buyer_seller=buyer_seller, item=auction).exists():
            rating = Rating.objects.create(buyer_seller=buyer_seller, item=auction, rating=rating_value)
            return redirect('website:live_auction_items')
        else:
            return render(request, 'rating_already_submitted.html', {'buyer_seller': buyer_seller, 'auction': auction})

    return render(request, 'seller_rating.html', {'buyer_seller': buyer_seller, 'auction': auction})

def seller_profile(request, seller_id):
    seller = get_object_or_404(Buyer_Seller, user_id=seller_id)
    return render(request, 'seller_profile.html', {'seller': seller})

def refund_request(request):
    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            return redirect('userProfile:home')  # Redirect to a success page
    else:
        form = RefundRequestForm()
    return render(request, 'refund.html', {'form': form})

# In views.py
from django.http import HttpResponse
from django.template.loader import render_to_string

# In views.py
from django.http import HttpResponse
from django.template.loader import render_to_string

def generate_bill(request):
    # Logic to generate the bill (You need to implement this)
    # For demonstration purposes, I'll render a simple bill template
    context = {
        'customer_name': 'John Doe',
        'total_amount': 100.00,
        # Add other bill data here
    }
    html_content = render_to_string('bill_template.html', context)
    
    # Generate PDF from HTML content (You need to implement this)
    # For demonstration, we'll just return HTML content
    return HttpResponse(html_content, content_type='text/html')

