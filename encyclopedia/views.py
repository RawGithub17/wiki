from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms

from . import util
import markdown2
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

#convert to markdown for every page
def entry(request, entry):
    entry_md = util.get_entry(entry)
    if entry_md == None:
        return render(request,'encyclopedia/error.html', {'error' : "Page not found"})
    return render(request, 'encyclopedia/entry.html', {
        'content': markdown2.markdown(entry_md),
        'title': entry
    })

#deliberately typing /search breaks becasue of GET
def search(request):
    if request.method == "POST":
        query = request.POST.get('q')
        entries = util.list_entries()
        matches = []

        #exact name found
        if duplicates(query):
            return HttpResponseRedirect(reverse('encyclopedia:entry', args=[request.POST['q']]))

        for entry in entries:                
            if query.casefold() in entry.casefold():
                matches.append(entry)

        return render(request, 'encyclopedia/search.html', {
            'matches':matches,
            'query' : query
        })
    else:
        return render(request, "encyclopedia/error.html", {'error': 'Please utilize the search bar in order to search'})

#bug: every edit makes the .md file more spaced out?
def edit(request, entry):
    if request.method == 'POST':
        #submits a change
        edit_form = EditForm(request.POST)
        if edit_form.is_valid():
            util.save_entry(entry, edit_form.cleaned_data["content"])
            return HttpResponseRedirect(reverse('encyclopedia:entry', args=[entry])) 
    else:
        #gets user to the edit page and changes the textbox properly
        content_md = util.get_entry(entry)
        data = {'content' : content_md}
        return render(request, "encyclopedia/edit.html", {
            'title':entry, 'form': EditForm(data)
        })
def new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            #check if that title exists already
            if not duplicates(title):
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('encyclopedia:entry', args=[title]))
            else:
                return render(request, 'encyclopedia/new.html', {'form' : form, 'taken' : True})
    return render(request, 'encyclopedia/new.html', {
        'form' : PostForm(),
        'taken' : False
    })

def random_page(request):
    entries = util.list_entries()
    page = random.choice(entries)
    return HttpResponseRedirect(reverse('encyclopedia:entry', args=[page]))

def duplicates(query):
    entries = util.list_entries()
    for entry in entries:
        if entry.casefold() == query.casefold():
            return True
    return False



class PostForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class' : 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))

