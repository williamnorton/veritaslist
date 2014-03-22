from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from alpha.models import List, Choice
from django.core.urlresolvers import reverse
from django.utils import timezone
from time import localtime, strftime

# Create your views here.


def index(request):
	"""
	In the future, 	if the user is not logged in, go to a login page

					else

					Show the main index page
	"""
	recent_lists = List.objects.order_by('-pub_date')[:5]
	template = loader.get_template('alpha/index.html')
	context = RequestContext(request,	{'recent_lists': recent_lists, })
	return render(request, 'alpha/index.html', context)

def detail(request, list_id):
	if request.method=="POST":
		choiceid = request.POST['choiceid']
		choicechecked = request.POST['choicechecked']
		vlist = get_object_or_404(List, pk=list_id)
		

		vchoice = Choice.objects.get(id=choiceid)
		vchoice.isChecked = not vchoice.isChecked 
		vchoice.save()
		
		return HttpResponseRedirect(reverse('detail', args=(vlist.id,)))
		#return render(request, 'alpha/detail.html', {'vlist': vlist, 'error_message': "CHANGE MADE??"+choiceid+vchoice.isChecked})
	else:
		vlist = get_object_or_404(List, pk=list_id)
		return render(request, 'alpha/detail.html', {'vlist': vlist})

def listcreator(request):
	"""
	In the future, check if user is logged in
	"""
	return render(request, 'alpha/listcreator.html',{'filler': "asdfd"})

def handle_post(request):
	"""
	When the user makes a new list from listcreator, they go here
	Redirect to the list after five seconds?

	Use the vote method as a template, we're using POST data I think
	"""
	try:
		confirmation = request.POST['confirmation']
		checklist_type = request.POST['listtype']
	except (KeyError):
		return render(request, 'alpha/listcreator.html', {
			'error_message': "Please select a checklist type, and confirm your decision"})
	else:
		"""Make a new list here"""	
		listname=str(checklist_type.capitalize())+": "+str(strftime("%a, %B %d, at %H:%M",localtime()))
		newlist = List(name=listname, pub_date=timezone.now())
		newlist.save()
		populate_list(newlist)
		return HttpResponseRedirect(reverse('success'))

def success(request):
	return render(request, 'alpha/success.html',{'filler': "asdfd"})


def populate_list(vlist):
	if vlist.name.startswith("Ga"):
		g = vlist.choicegroup_set.create(group_text="Control Room")
		g.choice_set.create(choice_text="Gamma Question 1")	
		g.choice_set.create(choice_text="Gamma Question 2")	
		g.choice_set.create(choice_text="Gamma Question 3")	
	elif vlist.name.startswith("Be"):
		vlist.choice_set.create(choice_text="Beta Question 1")	
		vlist.choice_set.create(choice_text="Beta Question 2")	
		vlist.choice_set.create(choice_text="Beta Question 3")	
	elif vlist.name.startswith("Al"):
		vlist.choice_set.create(choice_text="Alpha Question 1")	
		vlist.choice_set.create(choice_text="Alpha Question 2")	
		vlist.choice_set.create(choice_text="Alpha Question 3")	
