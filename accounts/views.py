from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, home.html)
    
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('dashboard')  
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login') 

@login_required
def dashboard(request):
    tools = [
        {'name': 'Pairwise Alignment', 'url': '/pairwise_alignment/'},
        {'name': 'Multiple Sequence Alignment', 'url': '/multiple_alignment/'},
        {'name': 'GC Content Calculator', 'url': '/gc_content/'},
        {'name': 'Codon Usage Calculator', 'url': '/codon_usage/'},
        {'name': 'Data Compression Tool', 'url': '/data_compression/'},
        {'name': 'MusicDNA', 'url': '/musicdna/'},
    ]
    return render(request, 'dashboard.html', {'tools': tools})
