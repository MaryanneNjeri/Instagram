from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm,ImageForm,SignUpForm,UserForm,CommentForm
from .models import Profile,Image,Comment
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.contrib.auth import login,authenticate
# Create your views here.
def signup(request):
    if request.method == 'POST':
        form=SignUpForm(request.POST,request.FILES)
        if form.is_valid():
            user=form.save()
            user.refresh_from_db()
            user.profile.name=form.cleaned_data.get('name')

            user.profile.Bio=form.cleaned_data.get('Bio')

            user.profile.profile_image=form.cleaned_data.get('profile_image')
            user.save()

            raw_password=form.cleaned_data.get('password1')
            user=authenticate(username=user.username,password=raw_password)
            login(request, user)

    else:
        form=SignUpForm()
    return render (request,'signup.html',{'form':form})
@login_required(login_url='/accounts/login')
def home(request):
    title='Welcome to Instaphoto'
    current_user=request.user
    profile_info=Profile.objects.all()
    profile=Profile.objects.get(user=current_user)
    images=Image.objects.all()
    return render(request,'main/home.html',{"title":title,"profile_info":profile_info,"images":images})
@login_required(login_url='/accounts/login')
def index(request):
    title='Welcome to instagram'


    return render(request,'main/index.html',{"title":title})
@login_required
def first_profile(request,profile_id):
    current_profile=Profile.objects.get(id=profile_id)
    try:
        profile_info =Profile.objects.get(id=profile_id)
    except DoesNotExsist:
        raise Http404()

    images =Image.objects.filter(profile=current_profile)

    return render(request,'main/profile.html',{"profile_info":profile_info,"images":images})

def add_image(request):

   profiles=Profile.get_profile()
   for profile in profiles:
       form=ImageForm(request.POST,request.FILES)
       if request.method == 'POST':
           if form.is_valid():
            image=form.save(commit=False)
            image.profile=profile
            image.save()
            return redirect(first_profile,profile.id)

   else:
        form=ImageForm()

   return render(request,'main/image.html',{"form":form})
'''
we set is_liked=false thus it will present the like button but if the exists a user id
 in the likes then is liked is set to true thus the button presented is dislike
'''
def details(request,image_id):
    current_image=Image.objects.get(id=image_id)
    images=Image.objects.get(id=image_id)
    is_liked=False
    if images.likes.filter(id=request.user.id).exists():
        is_liked = True

    try:
        image_details = Image.objects.get(id=image_id)
    except DoesNotExsist:
        raise Http404()



    comment_details=Comment.objects.filter(image=current_image)

    return render(request,'main/details.html',{"image_details":image_details,"comment_details":comment_details,"images":images,"is_liked":is_liked,"total_likes":images.total_likes()})

def search_profile(request):
    search_term=request.GET.get("profile")
    searched_profiles=Profile.search(search_term)
    return render (request,'main/search.html',{"searched_profiles":searched_profiles})
def nav(request,profile_id):
    title='hello'
    profile_info=Profile.objects.get(id=profile_id)
    return render(request,'navbar1.html',{"profile_info":profile_info})
def comment(request,image_id):
    current_user= request.user
    current_image=Image.objects.get(id=image_id)

    if request.method == 'POST':
        form=CommentForm(request.POST,request.FILES)
        if form.is_valid():
            comment_form=form.save(commit=False)
            comment_form.user=current_user
            comment_form.image=current_image
            comment_form.save()

    else:
            form=CommentForm()

    return render (request ,'main/comment.html',{"form":form,"current_image":current_image})
'''
we set is_liked to false thus the like button is presented and when clicked they are removed from the db
 if they exist we remove them from the db
else we add them and is like is true thus presenting the dislike button
'''
def like_post(request,image_id):
    post=Image.objects.get(id=image_id)
    is_liked=False
    if post.likes.filter(id=request.user.id).exists() :
        post.likes.remove(request.user)
        is_liked = False
    else:
        post.likes.add(request.user)
        is_liked=True
    return redirect(details,post.id)
