from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from beta.models import List, Choice
from django.core.urlresolvers import reverse
from django.utils import timezone
from time import localtime, strftime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError


# Create your views here.


def index(request):
	if request.method=="POST":
		username = request.POST['username']
		password = request.POST['password']
		user=authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
			else:
				return HttpResponseRedirect(reverse('login'))
		else:
			return render(request, 'beta/login.html', {'error_message': "Incorrect Username/PIN"})
				
	if not request.user.is_authenticated():
		return render(request, 'beta/login.html', {'error_message': "Please log in"})
	
	recent_lists = List.objects.order_by('-pub_date')[:5]
	older_lists = List.objects.order_by('-pub_date')[5:15]
	template = loader.get_template('beta/index.html')
	context = RequestContext(request,	{'recent_lists': recent_lists, 'older_lists': older_lists })
	return render(request, 'beta/index.html', context)

def login_view(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('index'))
		
	return render(request, 'beta/login.html', RequestContext(request, {"blank": "nothing"}))

def detail(request, list_id):
	if not request.user.is_authenticated():
		return render(request, 'beta/login.html', {'error_message': "Please log in"})
	if request.method=="POST":
		choiceid = request.POST['choiceid']
		choicechecked = request.POST['choicechecked']
		vlist = get_object_or_404(List, pk=list_id)
		if request.user.username not in vlist.observers_list:
			vlist.observers_list = vlist.observers_list + ", "+request.user.username

		vchoice = Choice.objects.get(id=choiceid)
		vchoice.isChecked = not vchoice.isChecked 
		
		last_change = str( strftime("%H:%M", localtime()))
		vchoice.last_date=last_change

		vchoice.last_user=request.POST['username']
		vchoice.save()

		return HttpResponseRedirect(reverse('detail', args=(vlist.id,)))
		#return render(request, 'beta/detail.html', {'vlist': vlist, 'error_message': "CHANGE MADE??"+choiceid+vchoice.isChecked})
	else:
		vlist = get_object_or_404(List, pk=list_id)
		return render(request, 'beta/detail.html', {'vlist': vlist})

@login_required(login_url='/beta/login/')
def listcreator(request):
	try:
		tree = ET.parse('master_checklist.xml')
	except IOError:
		return render(request, 'beta/listcreator.html',{'error_message': "IOError: master_checklist.xml not found"})	
	try:
		root = tree.getroot()
		checklist_list = []
		for checklist in root:
			checklist_list.append(checklist.get('name'))
	except ParseError:
		return render(request, 'beta/listcreator.html',{'error_message': "ParseError: master_checklist.xml was not well-formed"})	
		
	return render(request, 'beta/listcreator.html',{'checklists': checklist_list})

@login_required(login_url='/beta/login/')
def handle_post(request):
	#Handle POST data from listcreator. Create a new list in the database,
	#using parsed data from the master_checklist.xml.
	try:
		confirmation = request.POST['confirmation']
		checklist_type = request.POST['listtype']
	except (KeyError):
		return render(request, 'beta/listcreator.html', {
			'error_message': "Please select a checklist type, and confirm your decision"})
	else:
		try:
			tree = ET.parse('master_checklist.xml')
		except IOError:
			return render(request, 'beta/listcreator.html',{'error_message': "IOError: master_checklist.xml not found"})	
		try:
			root = tree.getroot()
			for checklist in root:
				if checklist.get('name')==checklist_type:
					listname=str(checklist_type)+": "+str(strftime("%a, %B %d, at %H:%M",localtime()))
					newlist = List(name=listname, pub_date=timezone.now(), observers_list=request.user.username)
					newlist.observers_list=request.user.username
					newlist.save()
					populate_by_xml(newlist,checklist)
					return HttpResponseRedirect(reverse('success'))

		except ParseError:
			return render(request, 'beta/listcreator.html',{'error_message': "ParseError: master_checklist.xml was not well-formed"})	
		return HttpResponseRedirect(reverse('success'))

def success(request):
	return render(request, 'beta/success.html',{'last_id': List.objects.last().id})

def logout_view(request):
	logout(request)
	return render(request, 'beta/logout.html', {'filler': "Logout page"})

def print_friendly(request, list_id):
	return render(request, 'beta/print_friendly.html', {'vlist': List.objects.get(id=list_id)})





def populate_by_xml(newlist, checklist):
	#A nested loop that populates a list, taking a List model and
	#an Element from our XML parser
	for choicegroup in checklist:
		subtext=''
		if choicegroup.get('subtext'):
			subtext=choicegroup.get('subtext')
		g = newlist.choicegroup_set.create(group_text = choicegroup.get('name'),subtext = subtext)
		g.save()
		for choice in choicegroup:
			details=''
			if choice.get('details'):
				details=choice.get('details')
			g.choice_set.create(choice_text=choice.text, details=details)
	newlist.save()




















