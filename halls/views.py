from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.forms.utils import ErrorList
import urllib
import requests
import os

from .models import Hall, Video
from .forms import VideoForm, SearchForm

YOUTUBE_API_KEY = str(os.getenv('YOUTUBE_API_KEY'))


def home(request):
    recent_halls = Hall.objects.order_by('-id')[:3]
    popular_halls = [Hall.objects.get(pk=2), Hall.objects.get(pk=3), Hall.objects.get(pk=4)]
    return render(request, 'halls/home.html', {'recent_halls': recent_halls, 'popular_halls': popular_halls})


def dashboard(request):
    halls = Hall.objects.filter(user=request.user)
    print(len(halls))
    return render(request, 'halls/dashboard.html', {'halls': halls})


def add_video(request, pk):
    form = VideoForm()
    search_form = SearchForm()
    hall = Hall.objects.get(pk=pk)
    # print(YOUTUBE_API_KEY)
    if hall.user != request.user:
        raise Http404

    if request.method == 'POST':
        form = VideoForm(request.POST)
        if form.is_valid():
            video = Video()
            video.hall = hall
            video.url = form.cleaned_data['url']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')

            if video_id:
                video.youtube_id = video_id[0]
                response = requests.get(
                    f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&id={video_id[0]}&key={YOUTUBE_API_KEY}')
                items = response.json()['items']
                if items:
                    title = items[0]['snippet']['title']
                    video.title = title
                    video.save()
                    return redirect('detail_hall', pk)

            errors = form._errors.setdefault('url', ErrorList())
            errors.append('Needs to be a valid YouTube URL')

    return render(request, 'halls/add_video.html', {'form': form, 'search_form': search_form})


def video_search(request):
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        search_line = search_form.cleaned_data['search_line']
        search_line_encoded = urllib.parse.quote(search_line)
        response = requests.get(
            f'https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=6&q={search_line_encoded}&key={YOUTUBE_API_KEY}'
        )
        return JsonResponse(response.json())
    return JsonResponse({'error': 'Not able to validate form'})


class DeleteVideo(generic.DeleteView):
    model = Video
    template_name = 'halls/delete_video.html'
    success_url = reverse_lazy('dashboard')


class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view


class CreateHall(generic.CreateView):
    model = Hall
    fields = ['title']
    template_name = 'halls/create_hall.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateHall, self).form_valid(form)
        return redirect('dashboard')


class DetailHall(generic.DetailView):
    model = Hall
    template_name = 'halls/detail_hall.html'


class UpdateHall(generic.UpdateView):
    model = Hall
    template_name = 'halls/update_hall.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')


class DeleteHall(generic.DeleteView):
    model = Hall
    template_name = 'halls/delete_hall.html'
    success_url = reverse_lazy('dashboard')
