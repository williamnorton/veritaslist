from django.shortcuts import render, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse, Http404, HttpResponseRedirect
from beta.models import List, Choice
from django.core.urlresolvers import reverse
from django.utils import timezone
from time import localtime, strftime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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
	return render(request, 'beta/listcreator.html',{'filler': "asdfd"})

def handle_post(request):
	"""
	When the user makes a new list from listcreator, they go here
	Redirect to the list after five seconds?
	"""
	try:
		confirmation = request.POST['confirmation']
		checklist_type = request.POST['listtype']
	except (KeyError):
		return render(request, 'beta/listcreator.html', {
			'error_message': "Please select a checklist type, and confirm your decision"})
	else:
		"""Make a new list here"""	
		listname=str(checklist_type)+": "+str(strftime("%a, %B %d, at %H:%M",localtime()))
		newlist = List(name=listname, pub_date=timezone.now(), observers_list=request.user.username)
		newlist.observers_list=request.user.username
		newlist.save()
		populate_list(newlist)
		return HttpResponseRedirect(reverse('success'))

def success(request):
	return render(request, 'beta/success.html',{'last_id': List.objects.last().id})

def logout_view(request):
	logout(request)
	return render(request, 'beta/logout.html', {'filler': "Logout page"})

def print_friendly(request, list_id):
	return render(request, 'beta/print_friendly.html', {'vlist': List.objects.get(id=list_id)})

def populate_list(vlist):
	if vlist.name.startswith("End"):
		vlist.display_name="End-of-Night"+": "+str(strftime("%a, %B %d, at %H:%M",localtime()))

		g = vlist.choicegroup_set.create(group_text="Control Room (before telescopes/trailers)")
		g.save()
		g.choice_set.create(choice_text="On control03, turn off HV and exit the program")	
		g.choice_set.create(choice_text="Announce on NORMAL radio channel that VERITAS as completed observations")	
		g.choice_set.create(choice_text="On control03 send the telescopes to stow position")
		g.choice_set.create(choice_text="On control03 close the current monitor software")
		g.choice_set.create(choice_text="On control02 stop VDAQ: ssh to arrayctl.vts, ex. =E2=80=9CstopVDAQ.pl -1234=E2=80=9D")
		g.choice_set.create(choice_text="On control02 turn OFF all camera fans (if they were on): on arrayctl: stop_camera_fan -a")


		g = vlist.choicegroup_set.create(group_text="Telescope 1")
		g.save()
		g.choice_set.create(choice_text="Turn the key from LOCAL to OFF on both HV crates")	
		g.choice_set.create(choice_text="Turn OFF the preamp power supplies")
		g.choice_set.create(choice_text="Check that the camera fan is off (red light should be off)")
		g.choice_set.create(choice_text="Check that all 4 FADC crates are powered off (no lights on)")
		g.choice_set.create(choice_text="Switch off the chiller (DISABLE system and comp.) only if FADCs are off")
		g.choice_set.create(choice_text="Turn the trailer AC to 75 =C2=BAF")
		g.choice_set.create(choice_text="Close the internal door in the trailer")

		g = vlist.choicegroup_set.create(group_text="Telescope 2")
		g.save()
		g.choice_set.create(choice_text="Turn the key from LOCAL to OFF on both HV crates")	
		g.choice_set.create(choice_text="Turn OFF the preamp power supplies")
		g.choice_set.create(choice_text="Check that the camera fan is off (red light should be off)")
		g.choice_set.create(choice_text="Check that all 4 FADC crates are powered off (no lights on)")
		g.choice_set.create(choice_text="Switch off the chiller (DISABLE system and comp.) only if FADCs are off")
		g.choice_set.create(choice_text="Turn the trailer AC to 75 =C2=BAF")

		g = vlist.choicegroup_set.create(group_text="Telescope 3")
		g.save()
		g.choice_set.create(choice_text="Turn the key from LOCAL to OFF on both HV crates")	
		g.choice_set.create(choice_text="Turn OFF the preamp power supplies")
		g.choice_set.create(choice_text="Check that the camera fan is off (red light should be off)")
		g.choice_set.create(choice_text="Check that all 4 FADC crates are powered off (no lights on)")
		g.choice_set.create(choice_text="Switch off the chiller (DISABLE system and comp.) only if FADCs are off")
		g.choice_set.create(choice_text="Turn the trailer AC to 75 =C2=BAF")

		g = vlist.choicegroup_set.create(group_text="Telescope 4")
		g.save()
		g.choice_set.create(choice_text="Turn the key from LOCAL to OFF on both HV crates")	
		g.choice_set.create(choice_text="Turn OFF the preamp power supplies")
		g.choice_set.create(choice_text="Check that the camera fan is off (red light should be off)")
		g.choice_set.create(choice_text="Check that all 4 FADC crates are powered off (no lights on)")
		g.choice_set.create(choice_text="Switch off the chiller (DISABLE system and comp.) only if FADCs are off")
		g.choice_set.create(choice_text="Turn the trailer AC to 75 =C2=BAF")


		g = vlist.choicegroup_set.create(group_text="Telescopes & trailers double checked to reduce danger of = serious damage (FADC meltdown, PMT exposure, etc).")
		g.save()
		g.choice_set.create(choice_text="Telescope 1 double checked")
		g.choice_set.create(choice_text="Telescope 2 double checked")
		g.choice_set.create(choice_text="Telescope 3 double checked")
		g.choice_set.create(choice_text="Telescope 4 double checked")
		

		g = vlist.choicegroup_set.create(group_text="ATO telescope: (not currently in use)")
		g.save()
		g.choice_set.create(choice_text="Verify the scope is in STOW position (if not, start up Xobs and stow it from the local terminal)")
		g.choice_set.create(choice_text="Turn off the two servo enable switches. ENSURE THE SERVOS ARE OFF until the next night")
		g.choice_set.create(choice_text="Roll the shed back, reinsert the pins, close the door")

		g = vlist.choicegroup_set.create(group_text="At the computer hardware shed (old control trailer by T4)")
		g.save()
		g.choice_set.create(choice_text="Turn off the =E2=80=9CT0=E2=80=9D infrared radiometer (switch on power strip in staircase box)")
		g.choice_set.create(choice_text="Put the cap back on the =E2=80=9CT0=E2=80=9D infrared radiometer")
		g.choice_set.create(choice_text='Put the cap back on the Allsky Cloud Monitor at "T0"')

		g = vlist.choicegroup_set.create(group_text="Control Room")
		g.save()
		g.choice_set.create(choice_text='On control03 choose "Select Flasher Run" from VAC')
		g.choice_set.create(choice_text='On control03 choose "End Night" from VAC and exit VAC n/a On harvester, stop the errorArchivingDemon: \n$ ssh harvester ;$ ./errorArchivingDemon_kill.sh')
		g.choice_set.create(choice_text='On control02 run nightsum on harvester and put the results in the 	ELog')
		g.choice_set.create(choice_text='On control02 copy/paste the text runlog from the Run Log Generator into the ELog')
		g.choice_set.create(choice_text='On control02 send the ELog')
		g.choice_set.create(choice_text='On control02 reset CFD thresholds if necessary (depending on moonlight)')
		g.choice_set.create(choice_text='On control01 close the L2 trigger GUI')

		g = vlist.choicegroup_set.create(group_text='Control Room (after telescope/trailer shutdown)')
		g.save()
		g.choice_set.create(choice_text='On control03 verify that all four telescope interlocks are on and then exit the tracking programme')
		g.choice_set.create(choice_text='On control02 verify that all four shutters are closed in the Pointing Monitor focal plane view')
		g.choice_set.create(choice_text='On control02 power off T1-T4 Pointing Monitors using Power Off All')
		g.choice_set.create(choice_text='On control02 after all Pointing Monitors have powered off, close the Pointing Monitor Control window')
		g.choice_set.create(choice_text='On control01 verify that all three FIRs are powered down (windows red) and close the FIR windows')
		g.choice_set.create(choice_text='On control01 verify that the Allsky monitor lid is on and close the Allsky Monitor window')
		g.choice_set.create(choice_text='Update the telescope operation time/moon status on the whiteboard in the control room.')

		g = vlist.choicegroup_set.create(group_text='In the Ready Room')
		g.save()
		g.choice_set.create(choice_text='If neccessary, update the telescope operations time on the board in the ready room for the next night. (Main building, basement)')







	elif vlist.name.startswith("Start"):
		vlist.display_name="Start-of-Night"+": "+str(strftime("%a, %B %d, at %H:%M",localtime()))
		g = vlist.choicegroup_set.create(group_text="(T>90) Telescope 1", 
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Inspect around the base of each telescope for obstructions")	
		g.choice_set.create(choice_text="For telescope 2 & 3, turn on the infrared radiometers")	
		g.choice_set.create(choice_text="Check that the RUN/SAFE switch is at SAFE (down)")
		g.choice_set.create(choice_text="Check that the lights inside the positioner pedestal are off")
		g.choice_set.create(choice_text="Check that camera shutters are closed")
		g.choice_set.create(choice_text="Check that the safety bar on the platform is not in the way of the quad arms, remove if necessary")
		g = vlist.choicegroup_set.create(group_text="(T>90) Telescope 2", 
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Inspect around the base of each telescope for obstructions")	
		g.choice_set.create(choice_text="For telescope 2 & 3, turn on the infrared radiometers")	
		g.choice_set.create(choice_text="Check that the RUN/SAFE switch is at SAFE (down)")
		g.choice_set.create(choice_text="Check that the lights inside the positioner pedestal are off")
		g.choice_set.create(choice_text="Check that camera shutters are closed")
		g.choice_set.create(choice_text="Check that the safety bar on the platform is not in the way of the quad arms, remove if necessary")
		g = vlist.choicegroup_set.create(group_text="(T>90) Telescope 3", 
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Inspect around the base of each telescope for obstructions")	
		g.choice_set.create(choice_text="For telescope 2 & 3, turn on the infrared radiometers")	
		g.choice_set.create(choice_text="Check that the RUN/SAFE switch is at SAFE (down)")
		g.choice_set.create(choice_text="Check that the lights inside the positioner pedestal are off")
		g.choice_set.create(choice_text="Check that camera shutters are closed")
		g.choice_set.create(choice_text="Check that the safety bar on the platform is not in the way of the quad arms, remove if necessary")
		g = vlist.choicegroup_set.create(group_text="(T>90) Telescope 4", 
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Inspect around the base of each telescope for obstructions")	
		g.choice_set.create(choice_text="For telescope 2 & 3, turn on the infrared radiometers")	
		g.choice_set.create(choice_text="Check that the RUN/SAFE switch is at SAFE (down)")
		g.choice_set.create(choice_text="Check that the lights inside the positioner pedestal are off")
		g.choice_set.create(choice_text="Check that camera shutters are closed")
		g.choice_set.create(choice_text="Check that the safety bar on the platform is not in the way of the quad arms, remove if necessary")

		g = vlist.choicegroup_set.create(group_text="(T>90) Trailer 1",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Key on the HV supplies (2 crates) to LOCAL")
		g.choice_set.create(choice_text="Check that the front and back FADC rack doors are latched closed")
		g.choice_set.create(choice_text="Switch on the chiller - ENABLE system and ENABLE comp.")
		g.choice_set.create(choice_text="Turn the trailer AC to 57 =C2=BAF")
		g.choice_set.create(choice_text="Check that the dehumidifier is running")
		g.choice_set.create(choice_text="Verify that the HV crates booted okay \n(display shows splash screen, +5V, +-12V, +48V LEDs lit)")
		g = vlist.choicegroup_set.create(group_text="(T>90) Trailer 2",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Key on the HV supplies (2 crates) to LOCAL")
		g.choice_set.create(choice_text="Check that the front and back FADC rack doors are latched closed")
		g.choice_set.create(choice_text="Switch on the chiller - ENABLE system and ENABLE comp.")
		g.choice_set.create(choice_text="Turn the trailer AC to 57 =C2=BAF")
		g.choice_set.create(choice_text="Check that the dehumidifier is running")
		g.choice_set.create(choice_text="Verify that the HV crates booted okay \n(display shows splash screen, +5V, +-12V, +48V LEDs lit)")
		g = vlist.choicegroup_set.create(group_text="(T>90) Trailer 3",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Key on the HV supplies (2 crates) to LOCAL")
		g.choice_set.create(choice_text="Check that the front and back FADC rack doors are latched closed")
		g.choice_set.create(choice_text="Switch on the chiller - ENABLE system and ENABLE comp.")
		g.choice_set.create(choice_text="Turn the trailer AC to 57 =C2=BAF")
		g.choice_set.create(choice_text="Check that the dehumidifier is running")
		g.choice_set.create(choice_text="Verify that the HV crates booted okay \n(display shows splash screen, +5V, +-12V, +48V LEDs lit)")

		g = vlist.choicegroup_set.create(group_text="(T>90) Trailer 4",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Key on the HV supplies (2 crates) to LOCAL")
		g.choice_set.create(choice_text="Check that the front and back FADC rack doors are latched closed")
		g.choice_set.create(choice_text="Switch on the chiller - ENABLE system and ENABLE comp.")
		g.choice_set.create(choice_text="Turn the trailer AC to 57 =C2=BAF")
		g.choice_set.create(choice_text="Check that the dehumidifier is running")
		g.choice_set.create(choice_text="Verify that the HV crates booted okay \n(display shows splash screen, +5V, +-12V, +48V LEDs lit)")


		g = vlist.choicegroup_set.create(group_text="(T>90) ATO Telescope",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Roll up the garage door")
		g.choice_set.create(choice_text="Turn off the two servo enable switches if they were left on")
		g.choice_set.create(choice_text="Remove the lock pins on the left and right side")
		g.choice_set.create(choice_text="Push on the two angled 2-by-4 to roll the shed as far back as it will go")
		g.choice_set.create(choice_text="Put the left lock pin through the angle bracket into the holes in the rail")
		g.choice_set.create(choice_text="Turn on the two servo enable switches")

		g = vlist.choicegroup_set.create(group_text="(T>90) In the computer hardware shed (old control trailer by T4)",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Remove the cap from the infrared radiometer (on staircase)")
		g.choice_set.create(choice_text="Turn on the radiometer - switch on power strip in box on staircase")

		g = vlist.choicegroup_set.create(group_text="(T>90) Main Building",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Switch off all unnecessary lights in the base camp buildings")
		g.choice_set.create(choice_text="Deploy all Venetian blinds and close all doors")

		g = vlist.choicegroup_set.create(group_text="(T>90) Control Room",
			subtext="NO LATER THAN 90 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="Turn on all camera fans: on arrayctl: start_camera_fan -a")
		g.choice_set.create(choice_text="Check that the CFD thresholds and Lookback Times are correct:\b ssh vdaq@dacq.t1	\n> vdbget_CFDSettings -t# (where #=3D1,2,3,4) threshold should be ~45mV,\n> vdbget_FADCChanSettings -t# (where #=3D1,2,3,4) lookback time should be 3000 samples")
		g.choice_set.create(choice_text="All observers should review the observing protocol for GRBs and the behavior of the GRB popup GUI, if they have not done so already this dark run. \nStart the errorArchivingDemon in a new terminal, and leave it running all night \n$ ssh harvester; ./errorArchivingDemon.run.sh")


		g = vlist.choicegroup_set.create(group_text="(T>75) Control Room: Control02 Computer",
			subtext="NO LATER THAN 75 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="On control02 check that ReadTemps is running on all four telescopes by opening readtemps desktop, and if necessary clicking on RT Icon \n(or Log into arrayctl and launch FADC temperature monitors: ssh arrayctl, startReadTemps.pl -1234)")
		g.choice_set.create(choice_text="On control02 launch the array monitor http://arraymon.vts (bookmarked as VTSSlowCtl)")
		g.choice_set.create(choice_text="On control02 (right desktop) launch DACQ.\n(This turns on the FADCs, so Chillers must be on first)\nssh to arrayctl.vts, ex. =E2=80=9CstartVDAQ.pl -1234=E2=80=9D")

		g.choice_set.create(choice_text="On control02 execute =E2=80=9Cgrb_play=E2=80=9D to test that the GRB alert sound is working")

		g = vlist.choicegroup_set.create(group_text="(T>75) Control Room: Control03 Computer",
			subtext="NO LATER THAN 75 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text="On control03 launch Tracking: click Trk Icon\n(or ex. =E2=80=9CstartTRK.pl =E2=80=93a=E2=80=9D),\ncheck to see that telescopes are in Array Mode.")
		g.choice_set.create(choice_text="On control03 launch VAC: (JAN 2014: ssh to arrayctl.vts, ex. =E2=80=9C VAC &=E2=80=9D)")
		g.choice_set.create(choice_text="Check for recent GRB alerts on the GRB panel of array_tracking")
		g.choice_set.create(choice_text="Check the highest energy Fermi photon to determine if data is to be taken for the photon during the night")
		g.choice_set.create(choice_text="After a few minutes check VAC to see that event builders are connected")
		g.choice_set.create(choice_text="In VAC, select Observer->Start Night")
		g.choice_set.create(choice_text="Check that VAC has connected to harvester, database and L3. L3 should be in the initialized state.")
		g.choice_set.create(choice_text='Check that sufficient disk space is free\nIn VAC: - Observer->Check Free Disk Space\nIn a terminal check UCLA raid space (>250GB):\n"$ ssh archiver@archive diskfree" (all one command)')

		g = vlist.choicegroup_set.create(group_text="(T>75) Control Room: Control01 Computer",
			subtext="NO LATER THAN 75 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text='On control01 launch the Infrared Radiometers: click on the FIR Icon\n(or ex. =E2=80=9CRUNFIR &=E2=80=9D); WAIT a minute for windows to appear')
		g.choice_set.create(choice_text='On control01 launch the All-Sky Cloud Monitor by clicking the All-Seeing Eye Icon\n(or execute, "vncviewer 10.0.0.143")\nClick on "Start Video", set an exposure time of ~10 sec.')
		g.choice_set.create(choice_text='On control01 launch the lidar http://lidar.vts (bookmarked).\nRight click on tab, "Reload Every" -> "Enable" and choose appropriate time interval.')

		g = vlist.choicegroup_set.create(group_text="(T>75) Control Room: L2 Trigger GUI",
			subtext="NO LATER THAN 75 MINUTES BEFORE STARTUP")
		g.save()
		g.choice_set.create(choice_text='On control01 start the L2 trigger GUI by typing:\njava -jar /home/observer/L2Software/L2TriggerGUI.jar')
		g.choice_set.create(choice_text='Click the "Connect to CORBA Servers" button in the "Monitoring" tab.')
		g.choice_set.create(choice_text='In the "Configuration" tab of the GUI, check that all pixels in each telescope are either inverted and enabled or un-inverted and disabled.\nThis can be done by clicking the "Refresh All Pixels" button.\nAll pixels should be either green or black.\nThere should be NO blue pixels')
		g.choice_set.create(choice_text='Check that there are no stuck on pixels by clicking the "Check for triggered/stuck pixels" button in the "Configuration" tab. Any pixels that show up as red should be disabled and un-inverted.\nNote: If the FADCs are not powered on, all pixels will appear red.')
		g.choice_set.create(choice_text='In the "Configuration" tab check that the detune is on(green color on the circular mark besides of on/off button), and the L2 Output width is set to 5.')
		g.choice_set.create(choice_text='In the "Monitoring" tab, from the "All" view, click the "Read Timing Alignment Info" button.\n\nView the delay settings for each telescope by selecting "Delays" in the drop-down menu.\n\nEnsure that delays are loaded (i.e., the pixels have non-zero delay values.) for each telescope.  For more information on verifying the timing alignments are loaded properly, see: http://veritas.sao.arizona.edu/wiki/index.php/ANL/ISU_L2#Verifying_a_Timing_Alignment_Is_Loaded')

		g = vlist.choicegroup_set.create(group_text="(T>45) Inside trailer 1",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Turn the preamps ON. Verify that they are delivering ~350W')
		g = vlist.choicegroup_set.create(group_text="(T>45) Inside trailer 2",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Turn the preamps ON. Verify that they are delivering ~350W')
		g = vlist.choicegroup_set.create(group_text="(T>45) Inside trailer 3",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Turn the preamps ON. Verify that they are delivering ~350W')
		g = vlist.choicegroup_set.create(group_text="(T>45) Inside trailer 4",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Turn the preamps ON. Verify that they are delivering ~350W')

		g = vlist.choicegroup_set.create(group_text="(T>45) Control Room",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='On control03 launch Current Monitor: click on the IMon Icon (or =E2=80=9CstartIMon.pl -1234=E2=80=9D)')
		g.choice_set.create(choice_text='On control03 launch HV: click HV Icon\n(or execute =E2=80=9CstartHV.pl -1234a=E2=80=9D)')
		g.choice_set.create(choice_text='Turn the HV on (PMT->All On), current monitors should read ~0.')
		g.choice_set.create(choice_text='Take a 2-minute fake flasher run:')
		g.choice_set.create(choice_text='Start the flasher \n( $ ssh arrayctl ; $ flasher )')
		g.choice_set.create(choice_text='Start a standard flasher run in VAC and make sure all sub-systems are working fine')
		g.choice_set.create(choice_text='Monitor the data being taken with quicklook ssh harvester, then run "ql_monitor".')
		g.choice_set.create(choice_text='If there is a Star Party or other activity outside the gate, read Overview of Observing. Talk to people/hand out flyers if necessary.')

		g = vlist.choicegroup_set.create(group_text="(T>45) Control Room",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='On control03 turn off HV')
		g.choice_set.create(choice_text='On control02 launch Pointing Monitor control: in VPM Control desktop click Vpm\n(or ssh in control04 and execute =E2=80=9Cvpmctl=E2=80=9D).\nPower on and start all monitors.')
		g.choice_set.create(choice_text='Start the ELog in your favorite text editor')

		g = vlist.choicegroup_set.create(group_text="(T>45) Telescope 1",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Check that lights on QI power supplies are off (switch should be kept ON)')
		g.choice_set.create(choice_text='Check that the red light on the fan power supply is on.')
		g.choice_set.create(choice_text='Turn on shutter power and open the shutter using the remote control')
		g.choice_set.create(choice_text='Replace the remote control and switch off shutter power')
		g.choice_set.create(choice_text='Turn off all the lights in the trailer')
		g.choice_set.create(choice_text='Check that internal door is closed')
		g.choice_set.create(choice_text='Flip the RUN/SAFE switch on positioner to =E2=80=9CRUN=E2=80=9D')


		g = vlist.choicegroup_set.create(group_text="(T>45) Telescope 2",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Check that lights on QI power supplies are off (switch should be kept ON)')
		g.choice_set.create(choice_text='Check that the red light on the fan power supply is on.')
		g.choice_set.create(choice_text='Turn on shutter power and open the shutter using the remote control')
		g.choice_set.create(choice_text='Replace the remote control and switch off shutter power')
		g.choice_set.create(choice_text='Turn off all the lights in the trailer')
		g.choice_set.create(choice_text='Check that internal door is closed')
		g.choice_set.create(choice_text='Flip the RUN/SAFE switch on positioner to =E2=80=9CRUN=E2=80=9D')
		
		g = vlist.choicegroup_set.create(group_text="(T>45) Telescope 3",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Check that lights on QI power supplies are off (switch should be kept ON)')
		g.choice_set.create(choice_text='Check that the red light on the fan power supply is on.')
		g.choice_set.create(choice_text='Turn on shutter power and open the shutter using the remote control')
		g.choice_set.create(choice_text='Replace the remote control and switch off shutter power')
		g.choice_set.create(choice_text='Turn off all the lights in the trailer')
		g.choice_set.create(choice_text='Check that internal door is closed')
		g.choice_set.create(choice_text='Flip the RUN/SAFE switch on positioner to =E2=80=9CRUN=E2=80=9D')

		g = vlist.choicegroup_set.create(group_text="(T>45) Telescope 4",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='Check that lights on QI power supplies are off (switch should be kept ON)')
		g.choice_set.create(choice_text='Check that the red light on the fan power supply is on.')
		g.choice_set.create(choice_text='Turn on shutter power and open the shutter using the remote control')
		g.choice_set.create(choice_text='Replace the remote control and switch off shutter power')
		g.choice_set.create(choice_text='Turn off all the lights in the trailer')
		g.choice_set.create(choice_text='Check that internal door is closed')
		g.choice_set.create(choice_text='Flip the RUN/SAFE switch on positioner to =E2=80=9CRUN=E2=80=9D')

		g = vlist.choicegroup_set.create(group_text="(T>45) Allsky cloud monitor",
			subtext='NO LATER THAN 45 MINUTES BEFORE STARTUP.')
		g.save()
		g.choice_set.create(choice_text='After sunset, open the cover for the allsky cloud monitor at T0')

		g = vlist.choicegroup_set.create(group_text="(T=0) Startup")
		g.save()
		g.choice_set.create(choice_text='Final check: outside - is the sun down / basecamp lights out?')
		g.choice_set.create(choice_text='Slew to zenith (85=C2=BA), then start slewing to the first source of the night. You want to be on target and tracking before astronomical twilight. Every minute of observing time counts.')
		g.choice_set.create(choice_text='Check that the 2 main radios in the Control Room are respectively on the "Normal"  and "VERITAS" bands.')
		g.choice_set.create(choice_text='Make sure the volume are set appropriately (we turn it down during the day)')
		g.choice_set.create(choice_text='Announce over the radio that VERITAS is turning on.')
		g.choice_set.create(choice_text='Turn the HV on in hvac (PMT->All On), watch the current monitors.')
		g.choice_set.create(choice_text='During first run, perform a "During Night" checklist')


	elif vlist.name.startswith("al"):
		g = vlist.choicegroup_set.create(group_text="Alpha Auxilliary List")
		g.save()
		g.choice_set.create(choice_text="I'm givin' her all she's got, Capt'n!")
