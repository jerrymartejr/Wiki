from django.shortcuts import render
import markdown2
from django.http import HttpResponseRedirect
from django import forms
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from random import choice

from . import util

# form for creating a new page
class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title", label_suffix="")
    content = forms.CharField(widget=forms.Textarea(attrs={"rows":"10"}), label="Content", label_suffix="")

    def clean_title(self):
        data = self.cleaned_data["title"]

        #check if title is already in the list of entries
        if data in util.list_entries():
            raise ValidationError(_("Title already exists"))

        return data

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# Entry Page
def entry(request, title):
    md = util.get_entry(title)

    if title in util.list_entries():
        #convert md to html
        content = markdown2.markdown(md)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "content": content
        })
    else:
        return render(request, "encyclopedia/pagenotfound.html")

# Search
def search(request):
    # get the data from form
    dic = request.GET
    q = dic["q"]

    # list of search results if query does not match the name of an encyclopedia entry
    results = []

    if q in util.list_entries():
        return HttpResponseRedirect(f"/wiki/{q}")
    else:
        for entry in util.list_entries():
            if q in entry:
                results.append(entry)
        return render(request, "encyclopedia/search.html", {
            "results": results
        })

# New Page
def new(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            # title = form.cleaned_data["title"]
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(f"/wiki/{title}")
        else:
            return render(request, "encyclopedia/new.html", {
                "form": form
            })
    return render(request, "encyclopedia/new.html", {
        "form": NewEntryForm()
    })

# Edit Page
def edit(request):
    if request.method == "GET":
        dic = request.GET
        title = dic["title"]
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": content
    })


    if request.method == "POST":
        dic = request.POST
        title = dic["title"]
        content = dic["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(f"/wiki/{title}")

# Random Page
def random(request):
    entries = util.list_entries()
    entry = choice(entries)
    return HttpResponseRedirect(f"/wiki/{entry}")
    
    



