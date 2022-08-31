import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.http import JsonResponse
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import User, Post, Follower


def index(request):
    all_posts = Post.objects.all().order_by('-timestamp')
    
    return render(request, "network/index.html", {
        "post_page": do_pagination(request, all_posts)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)

        # if picture got uploaded save it
        try:
            picture = request.FILES["picture"]
            user.picture = picture
            user.save()
        except MultiValueDictKeyError:
            pass
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


def profile_view(request, user_id):
    user = get_user_by_id(user_id)
    if request.user is authenticate:
        is_follower = get_user_follower(request, user)
    else:
        is_follower = False
    all_posts = user.posts.all().order_by('-timestamp')
    return render(request, "network/profile.html", {
        "profile": user,
        "is_follower": is_follower,
        "post_page": do_pagination(request, all_posts)
    })


@login_required(login_url='login')
def following_view(request):
    users_following = request.user.following_user.all()
    all_posts = Follower.objects.none()
    for follow in users_following:
        # merge two sets
        all_posts = all_posts | follow.following.posts.all()
    # perform queryset operation to sort by date
    ordered_posts = all_posts.distinct().order_by("-timestamp")
    return render(request, "network/following.html", {
        "post_page": do_pagination(request, ordered_posts)
    })


@login_required(login_url='login')
def newPost(request):
    if request.method == "POST":
        content = request.POST["content"]
        if len(content) == 0:
            #Post has no content
            return HttpResponseRedirect(reverse("index"))
        Post.objects.create(creator=request.user, content=content)
    return HttpResponseRedirect(reverse("index"))


@csrf_exempt
def is_liked(request, post_id):
    # Query for requested post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Update whether post is liked and returns new like amount
    if request.method == "PUT":
        data = json.loads(request.body)
        if data["liked"] == "yes":
            post.like.add(request.user)
        elif data["liked"] == "no":
            post.like.remove(request.user)
        else:
            return JsonResponse({"error": "Data not found."}, status=404)
        post.save()
        new_likes = len(post.like.all())
        return JsonResponse({
            "newLikes": new_likes
        }, status=201)

    else:
        return JsonResponse({
            "error": "PUT request required."
        }, status=400)


@csrf_exempt
def is_follower(request, profile_id):
    # Query for requested user
    try:
        profile = User.objects.get(pk=profile_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Return if user is a follower
    if request.method == "GET":
        follows_profile = get_user_follower(request, profile)
        return JsonResponse({"followsProfile": follows_profile}, status=201)

    # Update if user follows the profile
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data["follow"] == True:
            new_follower = Follower.objects.create(follower=request.user, following=profile)
            profile.followers.add(new_follower)
        elif data["follow"] == False:
            Follower.objects.filter(follower=request.user, following=profile).delete()
        else:
            return JsonResponse({"error": "Data not found."}, status=404)
        follower_count = profile.followers.all().count()
        return JsonResponse({"follower_count": follower_count}, status=201)        
    # must be via GET or PUT
    else:
        return JsonResponse({"error": "GET or PUT required"}, status=400)


@csrf_exempt
@login_required(login_url='login')
def edit(request, post_id):
    post = get_post_by_id(post_id)

    if request.user != post.creator:
        return JsonResponse({"error": "You are not the creator of this post!"}, status=400)

    elif request.method == "GET" :
        post_content = post.content
        return JsonResponse({"content": post_content}, status=201)

    elif request.method == "PUT":
        data = json.loads(request.body)
        if len(data["new_content"]) == 0:
            post.delete()
        else:
            post.content = data["new_content"]
            post.save()
        return HttpResponse(status=204)
        
    return JsonResponse({"error": "GET or PUT required"}, status=400)
    

def get_post_by_id(post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Bad Request: Post does not exist")
    return post


# Return if request.user follows the given user
def get_user_follower(request, user):
    if Follower.objects.filter(follower=request.user, following=user):
        return True
    else:
        return False


# returns the corresponding User to the given id
def get_user_by_id(user_id):
    try:
        user = User.objects.get(pk=user_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("Bad Request: User does not exist")
    return user


def do_pagination(request, posts):
    # gets the page, if not existing 1
    page_num = request.GET.get('page', 1)

    paginator = Paginator(posts, 10)
    try:
        post_page = paginator.page(page_num)
    except PageNotAnInteger:
        post_page = paginator.page(1)
    except EmptyPage:
        post_page = paginator.page(paginator.num_pages)
    return post_page
    

