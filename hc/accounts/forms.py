from django import forms


class LowercaseEmailField(forms.EmailField):

    def clean(self, value):
        value = super(LowercaseEmailField, self).clean(value)
        return value.lower()


class EmailPasswordForm(forms.Form):
    email = LowercaseEmailField()
    password = forms.CharField(required=False)


class ReportSettingsForm(forms.Form):
    report_period = forms.IntegerField(required=False)
    reports_allowed = forms.BooleanField(required=False)

class SetPasswordForm(forms.Form):
    password = forms.CharField()


class InviteTeamMemberForm(forms.Form):
    email = LowercaseEmailField()


class RemoveTeamMemberForm(forms.Form):
    email = LowercaseEmailField()


class TeamNameForm(forms.Form):
    team_name = forms.CharField(max_length=200, required=True)


class ReportConfigForm(forms.Form):
    period_choice = (
        ('0', 'Monthly'),
        ('1', 'Weekly'),
        ('2', 'Daily')
    )
    reports_allowed = forms.BooleanField(label="Send me a summary of my checks")
    report_period = forms.ChoiceField(widget=forms.RadioSelect, choices=period_choice)

