from django.shortcuts import render
from markdown import Markdown
from django import forms
from . import util
from django.http import HttpResponseRedirect
from django.urls import reverse
import random

class NewEntryForm(forms.Form):
    title = forms.CharField(label="New Title")
    content= forms.CharField(label="", widget=forms.Textarea)

class EditEntryForm(NewEntryForm):
    title = forms.CharField(label="")

def index(request):
    """
    Directs to index.html with a list of all entries
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def open_entry(request, title):
    """
    Directs to a page where the to HTML converted Markdown content
    of the given title gets displayed
    If the entry does not exist an error occurs
    """
    markdowner = Markdown()
    entry =  util.get_entry(title)
    if entry == None:
        entry = f"ERROR: There is no entry for {title} yet. Be the first to create one!"
        return render(request, "encyclopedia/no_entry.html", {
            "title": title,
            "entry": entry
        })
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "entry": markdowner.convert(entry)
        })

def search(request):
    """
    If the by the user provided query mathes to an existing 
    entry it redirects to that entry's page
    If the query is a substring of existing entries those
    entires will be shown on a result page
    """
    entries = util.list_entries()
    search_entry = request.GET['q']
    sub_list = []
    for i in range(len(entries)):
        if search_entry.lower() == entries[i].lower():
            return open_entry(request, search_entry)
        elif entries[i].lower().find(search_entry.lower()) > -1:
            sub_list.append(entries[i])
    return render(request, "encyclopedia/search.html", {
        "entries": sub_list,
        "search_entry": search_entry,
        "no_entries": len(sub_list) == 0
    })

def create(request):
    """
    Creates a form with which the user can create a new entry
    The entry already exist: Error
    Entry did not exist before: entry gets saved to disk and new entry
    page is opened
    """
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            entries = util.list_entries()
            for elem in entries:
                if title.lower() == elem.lower():
                    return render(request, "encyclopedia/entry.html", {
                        "title": title,
                        "entry": f"<h1>{title} already exists</h1>You can edit its entry by clicking the Edit button"
                    })
               
            util.save_entry(title, f"#{title} \n {content}")
            return HttpResponseRedirect(reverse("open_entry", kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/create.html", {
                "form": form
            })
    return render(request, "encyclopedia/create.html", {
        "form": NewEntryForm()
    })

def edit(request):
    """
    User can edit an entry's Markdown content
    After saving user gets redirected to the entry's page
    """
    if request.method == "POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            util.save_entry(title, form.cleaned_data["content"])
            return HttpResponseRedirect(reverse("open_entry", kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/edit.html", {
                "form": form
            })
    else:
        form = EditEntryForm()
        title = request.GET['q']
        form.fields["title"].initial = title
        form.fields["content"].initial = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "form": form,
        })

def random_page(request):
    """
    Directs to a random entry's page
    """
    entries = util.list_entries()
    title = entries[random.randint(0, len(entries)-1)]
    return HttpResponseRedirect(reverse("open_entry", kwargs={'title': title}))

