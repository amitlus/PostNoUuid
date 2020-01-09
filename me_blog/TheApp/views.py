from django.shortcuts import render, get_object_or_404, redirect
from TheApp.forms import UserForm, UserProfileInfoForm
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.generic import (View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from. import models
from TheApp.models import Post, Comment
from django.contrib.auth.mixins import LoginRequiredMixin
from TheApp.forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.utils import timezone


# Create your views here.
def index(request):
    return render(request, 'TheApp/index.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('TheApp:index'))


def register(request):

    registered = False

    if request.method == "POST":
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'profile_pic' in request.FILES:
                profile.profile_pic = request.FILES['profile_pic']

            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'TheApp/registration.html', {'user_form':user_form, 'profile_form':profile_form, 'registered':registered})

def user_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('TheApp:index'))

            else:
                return HttpResponse('ACCOUNT NOT ACTIVE')
        else:
            print("Someone tried to login and failed")
            print("Username: {} and password {}".format(username, password))
            return HttpResponse('invalid login details supplied')
    else:
        return render(request, 'TheApp/login.html',)







class PostListView(ListView):
    model = Post
    context_object_name = 'thelist'


    def get_queryset(self):
        return Post.objects.order_by('-create_date')
# בעצם מחזיר לי את הערכים כLIST שמסודר לפי תאריך היצירה מהחדש לישן.. בלי המינוס זה היה הפו


class PostDetailView(DetailView):
    model = Post

class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/' #attribute של הmixin .. אם מישהו לא מחובר זה מפנה אותו להתחבר
    redirect_field_name = 'TheApp/post_detail.html'
    form_class = PostForm  #במקום לציין fields
    model = Post

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.author= self.request.user #מכניס לו את המופע של User
        obj.save()
        return HttpResponseRedirect(obj.get_absolute_url())

#הפונקציה נקראת כש valid form ב-post.
#היא צריכה להחזיר HttpResponse
#בעצם הפונקציה הזו מגדירה את הערך של הauthor ובגלל שהורדתי אותו מה-Form אז הוא לא נראה לעין כשיוצרים פוסט חדש.
# אבל אוטומטית הערך שנכנס לauthor הוא היוזר המחובר.
#כשאני אסתכל ברשימת הפוסטים יהיה רשום מי יצר אותו



class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/TheApp/user_login' #attribute של הmixin .. אם מישהו לא מחובר זה מפנה אותו להתחבר
    redirect_field_name = 'TheApp/post_detail.html'
    form_class = PostForm
    model = Post

class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('TheApp:post_list')




############################################################################################



############################################################################################

@login_required
def add_comment_to_post(request,pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user.username
            comment.save()
            return redirect('TheApp:post_detail', pk=post.pk)
    else:
        form = CommentForm()
        return render(request, 'TheApp/comment_form.html', {'form':form})




@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    if (request.user.username == comment.author or request.user == comment.post.author): #רק אם המשתמש המחובר זה המשתמש שיצר את התגובה
        post_pk = comment.post.pk #מוסיפים את השורה הזו כי אחרי שנמחק את התגובה כבר לא נדע מה הPK שלה היה..
        comment.delete()
        return redirect('TheApp:post_detail', pk=post_pk)
    else:
         return HttpResponse('You are not the author of this comment. Access denied')
