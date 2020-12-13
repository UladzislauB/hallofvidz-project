from django import forms

from .models import Video


class VideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['url']
        labels = {
            'url': 'YouTube URL'
        }


class SearchForm(forms.Form):
    search_line = forms.CharField(max_length=255, label='Search for videos:')
