from django.shortcuts import render, redirect
from .models import Category, Photo
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail #for mail

from django.http import HttpResponseRedirect
from django.urls import reverse
# Create your views here.

from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm

from django.conf import settings


def home(request):
    return render(request, 'photos/home.html')

def loginUser(request):
    page = 'login'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('gallery')

    return render(request, 'photos/login_register.html', {'page': page})

def logoutUser(request):
      logout(request)
      return HttpResponseRedirect(reverse('home'))


def registerUser(request):
    page = 'register'
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            if user is not None:
                login(request, user)
                  #email part
                subject='Welcome to Photo Album!'
                message = f"Dear {user.username},\n\n"\
                        "Thank you for registering with Photo Gallery. "\
                        "We are excited to have you on board! "\
                        "If you have any questions or need assistance, "\
                        "feel free to reach out to us at primeinnovators@gmail.com.\n\n"\
                        "Regards,\n"\
                        "Prime Innovators"\
                        "9110459934"
                from_email='shubhamshastry@gmail.com'
                recipient_list=[user.email]
                send_mail(subject,message,from_email,recipient_list,fail_silently=False)
                return redirect('gallery')

    context = {'form': form, 'page': page}
    return render(request, 'photos/login_register.html', context)


@login_required(login_url='login')
def gallery(request):
    user = request.user
    category = request.GET.get('category')
    if category == None:
        photos = Photo.objects.filter(category__user=user)
    else:
        photos = Photo.objects.filter(
            category__name=category, category__user=user)

    categories = Category.objects.filter(user=user)
    context = {'categories': categories, 'photos': photos}
    return render(request, 'photos/gallery.html', context)


@login_required(login_url='login')
def viewPhoto(request, pk):
    photo = Photo.objects.get(id=pk)
    return render(request, 'photos/photo.html', {'photo': photo})


@login_required(login_url='login')
def addPhoto(request):
    user = request.user

    categories = user.category_set.all()

    if request.method == 'POST':
        data = request.POST
        images = request.FILES.getlist('images')

        if data['category'] != 'none':
            category = Category.objects.get(id=data['category'])
        elif data['category_new'] != '':
            category, created = Category.objects.get_or_create(
                user=user,
                name=data['category_new'])
        else:
            category = None

        for image in images:
            photo = Photo.objects.create(
                category=category,
                description=data['description'],
                image=image,
            )

             # Send email notification
        subject = 'Photo Uploaded'
        message = f"Dear {user.username},\n\n"\
                  "Your photo has been successfully uploaded to the photo gallery.\n\n"\
                  "Regards,\n"\
                  "Your Photo Gallery Team"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)


        return redirect('gallery')

    context = {'categories': categories}
    return render(request, 'photos/add.html', context)


from django.shortcuts import get_object_or_404

def deletePhoto(request, pk):
    photo = get_object_or_404(Photo, id=pk)
    if request.method == 'POST':
        photo.delete()
    return redirect('gallery')

