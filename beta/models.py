from django.db import models
from django.utils import timezone

# Create your models here.



class List(models.Model):
	name = models.CharField(max_length=200)
	display_name = models.CharField(max_length=30)
	pub_date = models.DateTimeField('date published')
	observers_list = models.CharField(max_length=60, default="")

	def __unicode__(self):
		return self.name

	def is_recent(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class ChoiceGroup(models.Model):
	parent = models.ForeignKey(List)
	group_text = models.CharField(max_length = 150)
	subtext = models.CharField(max_length=80, default=" ")

	def __unicode__(self):
		return self.group_text	
	
	def get_swatch(self):
		#Returns b if complete, c if totally incomplete, and d if partial
		total=0
		checked=0
		for choice in self.choice_set.all():
			total = total + 1
			if choice.isChecked:
				checked = checked + 1
		if checked==total:
			return "b"
		if checked==0:
			return "c"
		return "d"

class Choice(models.Model):
	parent = models.ForeignKey(ChoiceGroup)
	choice_text = models.CharField(max_length=200)
	isChecked = models.BooleanField(default=False)
	order_number = models.IntegerField(default=0)
	last_user = models.CharField(max_length=20, default="Nobody")
	last_date = models.CharField(max_length=10, default=' ')
	
	#details = models.CharField(max_length=150, default='')
	def __unicode__(self):
		return self.choice_text
