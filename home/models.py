from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save

# Create your models here.


durations = (
    ('m' , 'month'),
    ('s', 'six months'),
    ('y', 'year'),
)
duration_unit = (
    ('M' , 'month'),
    ('D', 'day'),
    ('Y', 'Year')
)
def addMonthToStartDate():
    return timezone.now() + timezone.timedelta(days=30)

class Coupon(models.Model):
    code = models.CharField(max_length=10)
    number_of_used_limite = models.IntegerField(default=0)
    number_of_used = models.IntegerField(default=0)
    trying_period = models.IntegerField(default=0)
    duration_unite = models.CharField(max_length=1, choices=duration_unit, default='D')
    trying_period_price = models.IntegerField(default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(auto_now_add=False)
    active = models.BooleanField(default=True)
    benifiters = models.ManyToManyField(User, blank=True, null=True,)

    def __str__(self):
        return self.code

class subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_duration = models.CharField(max_length=1, choices=durations)
    subscription_from = models.DateTimeField()
    subscription_to = models.DateTimeField()
    paid = models.BooleanField(default=False)
    price = models.FloatField(default=12.49)

    def __str__(self):
        return f"{self.user.username}'s subscription "

    def get_total_cost(self):
        return self.price


class profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_status = models.CharField(max_length=20, default="unactive")
    profile_subscription = models.ForeignKey(subscription, on_delete=models.SET_NULL, null=True, blank=True)
    coupon_code = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null = True, blank = True)



    def __str__(self):
        return f"{self.user.username}'s profile "

class settingModel2(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group_join_per_time= models.IntegerField(default=6)
    post_per_time = models.IntegerField(default=6)
    to_wait_after_each_join = models.IntegerField(default=12)
    to_wait_after_each_post = models.IntegerField(default=12)

    def __str__(self):
        return f'{self.user.username} settings'



def creatProfile(sender, **kwargs):
    if kwargs['created']:
        profile.objects.create(user=kwargs['instance'])

post_save.connect(creatProfile, sender=User)


def creatSetting(sender, **kwargs):
    if kwargs['created']:
        settingModel2.objects.create(user=kwargs['instance'])

post_save.connect(creatSetting, sender=User)

