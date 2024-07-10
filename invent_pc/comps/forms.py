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
