import json
from ast import literal_eval

from django import forms

from reader.models import Chapter, Group, Series


def preferred_sort_validity_check(preferred_sort):
    if not preferred_sort:
        return
    try:
        preferred_sort = literal_eval(preferred_sort)
    except Exception:
        raise forms.ValidationError("Invalid list for field 'Preferred sort'")
    if not (
        all(isinstance(group, str) and group.isdigit() for group in preferred_sort)
    ):
        raise forms.ValidationError(
            "List for field 'Preferred sort' has invalid elements. Must be string of valid group ids."
        )
    if Group.objects.filter(
        id__in=[int(group) for group in preferred_sort]
    ).count() != len(preferred_sort):
        raise forms.ValidationError(
            "One or more group ids specified in 'Preferred sort' is not associated with an actual group."
        )


class SeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        exclude = [
            id,
        ]

    def clean(self):
        preferred_sort_validity_check(self.cleaned_data.get("preferred_sort"))
        scraping_enabled = self.cleaned_data.get("scraping_enabled")
        if scraping_enabled:
            scraping_identifiers = self.cleaned_data.get("scraping_identifiers")
            try:
                scraping_identifiers = json.loads(scraping_identifiers)
            except Exception:
                raise forms.ValidationError(
                    "Invalid json for field 'Scraping identifiers'"
                )
        return self.cleaned_data


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        exclude = [
            id,
        ]

    def clean(self):
        preferred_sort_validity_check(self.cleaned_data.get("preferred_sort"))
        return self.cleaned_data
