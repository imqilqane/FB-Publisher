from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from ckeditor.fields import RichTextField
from embed_video.fields import EmbedVideoField

# Create your models here.

class Docs(models.Model):
    doc = RichTextField()
    video = EmbedVideoField(null=True, blank=True)   


class settingModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_price = models.FloatField(default=12.49)
    six_mounths_price = models.FloatField(default=64.94)
    yearly_price = models.FloatField(default=124.88)

    def __str__(self):
        return f'{self.user.username} settings'



class fbAccountsModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=20)
    fullname = models.CharField(max_length=60)
    dateOfCreating = models.CharField(max_length = 100, blank=True, null=True)
    accountStatus = models.CharField(max_length=12, default='active')

    def __str__(self):
        return self.fullname

class nichesModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    niche = models.CharField(max_length=100)
    skipQuestions = models.BooleanField(default=False)

    def __str__(self):
       return self.niche

class myGroupsModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    facebook_account = models.ForeignKey(fbAccountsModel, on_delete=models.CASCADE, null=True)
    group_name = models.CharField(max_length=200, blank=True, null=True)
    group_nich = models.CharField(max_length=200, blank=True, null=True)
    group_link = models.CharField(max_length=300, blank=True, null=True)
    posting_with_permestion = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    date_of_request = models.DateTimeField(default=timezone.now)
    favorated = models.BooleanField(default=False)
    privite_group = models.BooleanField(default=False)

    def __str__(self):
       return f"{self.group_name} in {self.facebook_account.username} facebook account"

    class Meta:
        ordering = ('-favorated',)

class testingPostsModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adCopy = models.CharField(max_length=200)

    def __str__(self):
        return f'{user.username} ad copies'

class imageGalery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField (default='' , upload_to='picturs' )
    nich = models.ForeignKey(nichesModel, on_delete=models.CASCADE, null=True)
    str_nich = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s image"
    
class copyWriting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.CharField (max_length=200)
    nich = models.ForeignKey(nichesModel, on_delete=models.CASCADE, null=True)
    str_nich = models.CharField(max_length=100, blank=True, null=True)


    def __str__(self):
        return f"{self.user.username}'s copyWriting"
    
class adCopy(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    descriprtion = models.CharField(max_length=200)
    link = models.CharField(max_length=100)
    image = models.ImageField (default='' , upload_to='picturs' , blank = True, null = True)
    niche = models.ForeignKey(nichesModel, on_delete=models.CASCADE, null=True)
    number_of_grouos_posted_in = models.IntegerField(default=0)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s ad copy"

class postedAdCompaigns(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    adcopy = models.ForeignKey(adCopy, on_delete=models.CASCADE)
    posting_group = models.ForeignKey(myGroupsModel, on_delete=models.CASCADE)
    fb_account = models.ForeignKey(fbAccountsModel, on_delete=models.CASCADE, null=True, blank=True)
    posted = models.BooleanField(default=False)
    post_link = models.CharField(max_length=200, null=True, blank=True)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    posted_at = models.DateTimeField(default=timezone.now)
    done = models.BooleanField(default=False)
    code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} posted {self.adcopy.link} in {self.posting_group.group_name}"

    class Meta:
        ordering = ('-posted_at',)

class linkToRemplace_to_toRemlaceWith(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_remplace = models.OneToOneField(copyWriting, on_delete=models.CASCADE)
    to_remplace_with = models.OneToOneField(postedAdCompaigns, on_delete=models.CASCADE)

    def __str__(sefl):
        return f"{self.user.username} posted {self.adcopy.link} in {self.posting_group.group_name}"

class adminCopywrits(models.Model):
    copy = models.CharField(max_length=200)

    def __str__(sefl):
        return sefl.copy