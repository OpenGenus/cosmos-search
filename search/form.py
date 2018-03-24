from django import forms
from .models import Votes


VOTES_CHOICES = [
    ('1', ''),
    ('2', ''),
    ['3', ''],
    ('4', ''),
    ('5', ''),
]


class VotesForm(forms.Form):
    project_name = forms.CharField(max_length=500, required=False)
    ip_address = forms.CharField(max_length=50, required=False)
    vote_value = forms.ChoiceField(VOTES_CHOICES, required=True,
                                   widget=forms.RadioSelect(attrs={"onclick": "this.form.submit();",
                                                                   "class": "votes",
                                                                   "data-fa-icon": "&#xf005"}))

    def save(self):
        u = Votes.objects.create(
            project_name=self.cleaned_data['project_name'],
            vote_value=self.cleaned_data['vote_value'],
            ip_address=self.cleaned_data['ip_address'],
        )
        u.save()
        return u
