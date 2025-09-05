from django.shortcuts import render
from . import util
import markdown2
import random

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):

    #keeping the original word formatting 
    for titles in util.list_entries():
        if titles.isupper() and titles == title.upper():
            title = title.upper()
            break
        else:
            title = title.capitalize()

    if util.get_entry(title) is None :
       return render(request, "encyclopedia/error.html", {
           "message": f"{title} was not found."
       })  
    else:
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "display" : markdown2.markdown(util.get_entry(title))
        })
    
def search(request):
    name = request.GET.get("q").strip()
    # first check if the name is in encyclopedia
    if util.get_entry(name) is None :
      
      # second check if the name is a substring of any item in list

      results = []

      for entries in util.list_entries():
          if name.lower() in entries.lower():
              results.append(entries)

      if len(results) > 0 :
          return render(request, "encyclopedia/search.html", {
        "display": results 
    })
      else:
          return render(request, "encyclopedia/error.html",  {
           "message": f"{name} was not found."
       })
    
       
    else:

        for titles in util.list_entries():
            if titles.isupper() and titles == name.upper():
                name = name.upper()
                break
            else:
                name = name.capitalize()

        return render(request, "encyclopedia/entry.html", {
            "title": name,
            "display": markdown2.markdown(util.get_entry(name))
        })
    
def newpage(request):
    if request.method == "POST":
        title = request.POST.get("title").strip()
        info = request.POST.get("information")
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/error.html",  {
           "message": f"{title} already exists."
       })
        else:
            util.save_entry(title,info)
            return render(request, "encyclopedia/entry.html", {
                "title": title,
                "display": markdown2.markdown(util.get_entry(title))
            })
        
    return render(request, "encyclopedia/newpage.html")    


def edit(request, entry):

    if request.method == "POST":
        info = request.POST.get("information")
        util.save_entry(entry, info)
        return render(request, "encyclopedia/entry.html", {
             "title": entry,
             "display": markdown2.markdown(util.get_entry(entry))
        })
    
    return render(request, "encyclopedia/edit.html", {
        "title": entry,
        "display":util.get_entry(entry)
    })

def random_entry(request):
    no_of_entries = len(util.list_entries())
    randomize = random.randint(0, no_of_entries-1)
    random_entry = util.list_entries()[randomize]
    return render(request, "encyclopedia/entry.html", {
             "title": random_entry,
             "display": markdown2.markdown(util.get_entry(random_entry))
        })