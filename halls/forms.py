from django import forms

from .models import Video


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'url', 'youtube_id']
        labels = {
            'youtube_id': 'YouTube Id'
        }


class SearchForm(forms.Form):
    search_form = forms.CharField(max_length=255, label='Search for videos:')
