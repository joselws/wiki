from django.shortcuts import render
from django import forms
from . import util
from django.urls import reverse
from django.http import HttpResponseRedirect
from random import randrange
import markdown2

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "search_entry_bar": SearchEntryForm()	#pass in a Django form to index.html
    })
    

class SearchEntryForm(forms.Form):
	"""define a django form for the main page search bar"""
	entry = forms.CharField(label="Search Page")
	
class CreateEntryForm(forms.Form):
	"""creates a django form to save a new entry"""
	title = forms.CharField(label="Page title")
	content = forms.CharField(label="Content of your page", widget=forms.Textarea)
		
	
def title(request, title):
	"""renders a wiki page from a specific title"""
	#If the user came from the search bar:
	if request.method == "GET":
		search = SearchEntryForm(request.GET)	#Search holds all the info from the search
		if search.is_valid():
			title = search.cleaned_data["entry"]	#if valid, title will be equal to what was put in the search
			
	#title holds the information of the wiki page which has the name of title
	#calls the get_entry function from util file for this process
	content = util.get_entry(title)
	
	#if the file does exist and we were able to successfully get its content
	if content:
		content = markdown2.markdown(content)	#convert content from markdown to html
		return render(request, "encyclopedia/title.html", {
			#pass in both the content and the title of the file to the page
			"title": title,
			"content": content
			})
	
	#if the file by the name of title doesn't exist, attempt to search for
	#possible files with similar names
	else:
		all_entries = util.list_entries()	#retrieve all list of entries
		successful_entries = []		#all matching similar entry names will be stored here
		
		for entry in all_entries:	#loops through all entries
			if title.lower() in entry.lower():		#if the user input from search matches characters from an existing entry
				successful_entries.append(entry)	#appends it as one of the possible matches
				
		if successful_entries:	#if the list is not empty, i.e. if there are query matches
			return render(request, "encyclopedia/results.html", {
				"matches": successful_entries,	#pass the list of matches to results.html
				"title": title		#and the search query
				})
		
		else: 	#go to an error page otherwise
			return render(request, "encyclopedia/missing.html", {
				"title": title
			})
			
			
def new(request):
	"""allow users to save a new html"""
	if request.method == "POST":	#if the user entered some data to create a new page
		new_page_data = CreateEntryForm(request.POST)	#new_page_data holds the data from the form
		if new_page_data.is_valid():		#server side validation
			title = new_page_data.cleaned_data["title"]		#retrieve data from the form
			content = new_page_data.cleaned_data["content"]
			
			if util.get_entry(title):		#displays an error page if the entry already exists
				return render(request, "encyclopedia/collision.html", {
					"title": title
					})
					
			else:	#create the new entry otherwise
				util.save_entry(title, content)
				return HttpResponseRedirect(reverse("index"))	#go to main page
				
		else:	#if data is not valid (didn't pass server-side validation)
			return render(request, "encyclopedia/new.html", {	#renders the 'new' page again
				"create_entry_form": CreateEntryForm()	#pass in the form to create a new title
				}) #go to the "create a new page" page

	else:	#if we don't get here by a post method
		return render(request, "encyclopedia/new.html", {
			"create_entry_form": CreateEntryForm()	#pass in the form to create a new title
			}) #go to the "create a new page" page
			
			
def random(request):
	"""takes the user to a random wiki page"""
	#retrieves a random element from the list of all wikis
	wiki_list = util.list_entries()
	index = randrange(len(wiki_list))	#retrieves a random index number from the list
	
	random_title = wiki_list[index]		#get a random title according to the random index number
	return HttpResponseRedirect(f"wiki/{random_title}")		#displays the page
	
		
def edit(request, title):
	"""Let user edit an existing markdown file"""
	content = util.get_entry(title)
	
	class EditEntryForm(forms.Form):
		"""Creates a django form to edit an existing entry"""
		content_form = forms.CharField(label="Content of your page", widget=forms.Textarea, initial=content)

	if request.method == "POST":							
		edit_entry = EditEntryForm(request.POST)			#get the data from the form
		if edit_entry.is_valid():							#if it passes server-side validation
			new_content = edit_entry.cleaned_data["content_form"]	#get the edited content from the data
			util.save_entry(title, new_content)				#overwrite the previous content
			return HttpResponseRedirect(f"../{title}")	#get the user to the newly edited entry
			
	else:													#go to the edit page if the user came via link
		return render(request, "encyclopedia/edit.html", {	#or url
			"title": title,
			"content": content,
			"edit_form": EditEntryForm()
			})
