from django.shortcuts import render,redirect
from .forms import *
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth import logout


# Create your views here.
def home(request):
    return render(request,'userProfile/home.html')

def aboutUs(request):
    return render(request,'userProfile/aboutUs.html')  

def register(request):
    if request.method=="POST":
        form=RegitrationForm(request.POST)
        if form.is_valid():
            var=form.save(commit=False)
            var.user=request.user
            var.save()
            return redirect ('userProfile:home')
    else:
        form=RegitrationForm()
    return render(request,'userProfile/register.html',{'form':form})

def profile_view(request):
    profile = request.user.buyer_seller
    #get_object_or_404(Buyer_Seller, user=request.user)
    return render(request,'userProfile/profile_view.html',{'profile':profile})


def profile_update(request):
    profile = Buyer_Seller.objects.get(user=request.user)

    if request.method == 'POST':
        form = RegitrationForm(request.POST, instance=profile)
        if form.is_valid():
            var=form.save(commit=False)
            var.user=request.user
            var.save()
            return redirect("userProfile:profile_view")
    else:
        form = RegitrationForm(instance=profile)

    return render(request, 'userProfile/profile_update.html', {'form': form})

