from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms

from . import util
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

#convert to markdown for every page
def entry(request, entry):
    entry_md = util.get_entry(entry)
    if entry_md == None:
        return render(request,'encyclopedia/entry.html', {'content' : "<h1>Page not found</h1>"})
    return render(request, 'encyclopedia/entry.html', {
        'content': markdown2.markdown(entry_md),
        'content_md': entry_md,
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

def edit(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        edited_content = request.POST.get('content')
        content_md = util.get_entry(title)

        if edited_content != None and edited_content != content_md:
            util.save_entry(title, edited_content)
            return HttpResponseRedirect(reverse('encyclopedia:entry', args=[title])) 
        else:
            data = {'content' : content_md}
            return render(request, "encyclopedia/edit.html", {
                'title':title, 'form': EditForm(data)
            })

    return HttpResponse("Error: please pick an entry and navigate properly to edit")

#NEEDS ERROR MESSAGE!!!!
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
                return render(request, 'encyclopedia/new.html', {'form' : PostForm()})


    return render(request, 'encyclopedia/new.html', {
        'form' : PostForm()
    })

def duplicates(query):
    entries = util.list_entries()
    for entry in entries:
        if entry.casefold() == query.casefold():
            return True
    return False

class PostForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)

class EditForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class' : 'form-control'}))

