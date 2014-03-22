from django.db import models
from django.utils import timezone

# Create your models here.



class List(models.Model):
	name = models.CharField(max_length=200)
	pub_date = models.DateTimeField('date published')

	def __unicode__(self):
		return self.name

	def is_recent(self):
		return self.pub_date >= timezone.now() - datetime.timedelta(days=1)

class ChoiceGroup(models.Model):
	parent = models.ForeignKey(List)
	group_text = models.CharField(max_length = 250)

	def __unicode__(self):
		return self.group_text	

class Choice(models.Model):
	parent = models.ForeignKey(ChoiceGroup)
	choice_text = models.CharField(max_length=250)
	isChecked = models.BooleanField(default=False)
	order_number = models.IntegerField(default=0)
	last_user = models.CharField(max_length=50)
	last_date = models.DateTimeField('Last Change Made')
	
	def __unicode__(self):
		return self.choice_text
