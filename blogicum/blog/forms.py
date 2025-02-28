from django.utils import timezone
from django import forms
from django.contrib.auth.models import User
from blog.models import Post, Location, Category, Comment


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CreatePostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True)
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True)
        self.fields['pub_date'].required = False
        self.fields['image'].required = False

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        # if pub_date and pub_date < timezone.now():
        #     raise forms.ValidationError("Дата публикации не может быть в
        # прошлом!")
        return pub_date

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.author = self.user
        if not instance.pub_date:
            instance.pub_date = timezone.now()
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pub_date': forms.DateInput(attrs={'class': 'form-control',
                                               'type': 'date'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EditPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(
            is_published=True)
        self.fields['category'].queryset = Category.objects.filter(
            is_published=True)
        self.fields['pub_date'].required = False
        self.fields['image'].required = False

    def clean_pub_date(self):
        pub_date = self.cleaned_data.get('pub_date')
        # if pub_date and pub_date < timezone.now():
        #     raise forms.ValidationError("Дата публикации не может быть в
        # прошлом!")
        return pub_date

    def save(self, commit=True):
        instance = super().save(commit=False)
        original_post = Post.objects.get(pk=instance.pk)
        if not instance.pub_date:
            instance.pub_date = original_post.pub_date
        instance.author = original_post.author
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'pub_date': forms.DateInput(attrs={'class': 'form-control',
                                               'type': 'date'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class AddCommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
