from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import Venue, Artist, Note, Show
from .forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, UserEditProfile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone



def user_profile(request, user_pk):
    user = User.objects.get(pk=user_pk)
    usernotes = Note.objects.filter(user=user.pk).order_by('posted_date').reverse()
    return render(request, 'lmn/users/user_profile.html', {'user' : user , 'notes' : usernotes })



@login_required
def my_user_profile(request):
    # TODO - editable version for logged-in user to edit own profile
    ##checked if the request is a post
    if request.method == 'POST':
        ##created the form with
        form = UserEditProfile(request.POST, instance=request.user)
        ##checked if the form was valid
        if form.is_valid():
            form.save()
            ##saved and refreshed page
            return HttpResponseRedirect(request.path_info)
        else:
            ##if the form is invalid this message will show
            message = 'Please check the data you entered'
            return render(request, 'lmn:users/edit_profile.html',{'form':form, 'message':message})
    else:
        ##else i just render the form
        form = UserEditProfile(instance=request.user)
        return render(request, 'lmn/users/edit_profile.html', {'form':form})

def register(request):

    if request.method == 'POST':

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            login(request, user)
            return redirect('lmn:homepage')

        else :
            message = 'Please check the data you entered'
            return render(request, 'registration/register.html', { 'form' : form , 'message' : message } )


    else:
        form = UserRegistrationForm()
        return render(request, 'registration/register.html', { 'form' : form } )
