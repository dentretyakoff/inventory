from django import forms

from comps.models import Department


class DepartmentFilterForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        label='',
        required=False,
        empty_label=None)

    class Meta:
        model = Department
        fields = ('department',)


class SearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=100, required=False, label='')
    older_days = forms.IntegerField(required=False, label='')
