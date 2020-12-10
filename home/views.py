from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate , login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from paypal.standard.forms import PayPalPaymentsForm
from django.urls import reverse
from .models import subscription, profile, settingModel2, Coupon
from facebook.models import settingModel
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import SubscriptionForm, settingsForm
from django.core.mail import EmailMessage
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_gen

def addMonthToStartDate():
    return timezone.now() + timezone.timedelta(days=30)

def addSixMonthToStartDate():
    return timezone.now() + timezone.timedelta(days=183)

def addYearToStartDate():
    return timezone.now() + timezone.timedelta(days=365)


# Create your views here.

def homeView(request):

    return render(request, 'home/index.html', {'title':'money crasher'})

def matchPass(pass1 , pass2):
    return pass1 == pass2

def registerView(request):
    if request.user.is_authenticated:
        return redirect('dash:dashboard')
    else:
        if request.method == 'POST':
            first_name = request.POST['fname']
            last_name = request.POST['lname']
            email = request.POST['email']
            username = request.POST['username']
            password1 = request.POST['password1']
            password2 =  request.POST['password2']

            
            if matchPass(password1, password2):
                new_user = User(
                    username = username,
                    first_name = first_name,
                    last_name = last_name ,
                    email = email ,
                )

                if len(password2) < 8 :
                    messages.warning(request, 'you password is too short ')
                    return redirect('home:register')
                
                try : 
                    User.objects.get(email=email)
                    messages.warning(request, 'this email is alredy exists')
                    return redirect('home:register')
                except:
                    pass
                
                try : 
                    User.objects.get(username=username)
                    messages.warning(request, 'this username is alredy exists')
                    return redirect('home:register')
                except:
                    pass


                new_user.set_password(password2)
                new_user.is_active = False
                new_user.save()
                print(password2)
                

                uidb64 = urlsafe_base64_encode(force_bytes(new_user.pk))
                domain = get_current_site(request).domain
                link = reverse('home:activate', kwargs={'uidb64':uidb64,'token':token_gen.make_token(new_user)})
                activate_url = f'http://{domain}{link}'

                email_body = f"hello {username} please use this link to verify your account {activate_url}"
                email = EmailMessage(
                    'Fb publisher activation email',
                    email_body,
                    'noreplay@fbpublisher.com',
                    [email,],
                )

                email.send(fail_silently=False)
                messages.success(request, "you've succesfully registerd, please check your inbox to verify your email and if you don't find the email in your inbox check spam folder too ")
                return redirect('home:home')
            else:
                messages.warning(request, 'passwords did not match')
                return redirect('home:register')

    context = {
        'title':'register'
    }

    return render(request, 'home/register.html', context)

def loginView(request):
    if request.user.is_authenticated:
        return redirect('dash:dashboard')
    else:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/dashboard')
            else :
                messages.warning(request, 'wrong password or username')
                return redirect('home:login')

    context = {
        'title':'login'
    }

    return render(request, 'home/login.html', context)

def vereficationView(request, uidb64, token):
    pk = urlsafe_base64_decode(uidb64)
    new_user = User.objects.get(id = pk)
    new_user.is_active = True
    new_user.save()

    messages.success(request, 'thanks for verifiy your account')
    return redirect('home:login')

@login_required
def logoutView(request):
    if not request.user.is_authenticated:
        messages.success(request, 'you\'re not loged in')
        return redirect('home:home')
    else:
        logout(request)
        messages.success(request, 'you\'re loged out')
        return redirect('home:login')
        

@login_required
def subscriptionView(request):
    if request.method == 'POST':
        f = SubscriptionForm(request.POST)
        if f.is_valid():
            request.session['subscription_plan'] = request.POST.get('plans')
            return redirect('home:process_subscription')
    else:
        f = SubscriptionForm()
    return render(request, 'home/subscription_form.html', locals())

@login_required
def process_subscription(request):
    superusers = User.objects.filter(is_superuser=True)
    admin_settings = settingModel.objects.get(user=superusers)
    subscription_plan = request.session.get('subscription_plan')
    host = request.get_host()
    
    if subscription_plan == '1-month':
        price = admin_settings.monthly_price
        billing_cycle = 1
        billing_cycle_unit = "M"
        the_sub = subscription.objects.create(
            user = request.user,
            subscription_duration = 'm',
            subscription_from = timezone.now(),
            subscription_to = addMonthToStartDate(),
            price = price
        )
        
    elif subscription_plan == '6-month':
        price = admin_settings.six_mounths_price
        billing_cycle = 6
        billing_cycle_unit = "M"
        the_sub = subscription.objects.create(
            user = request.user,
            subscription_duration = 's',
            subscription_from = timezone.now(),
            subscription_to = addSixMonthToStartDate(),
            price = price
        )
    else:
        price = admin_settings.yearly_price
        billing_cycle = 1
        billing_cycle_unit = "Y"
        the_sub = subscription.objects.create(
            user = request.user,
            subscription_duration = 'y',
            subscription_from = timezone.now(),
            subscription_to = addYearToStartDate(),
            price = price

        )
    the_profile = profile.objects.get(user=request.user)
    the_profile.profile_subscription = the_sub
    the_profile.save()

    if the_profile.coupon_code and the_profile.coupon_code.active and request.user not in the_profile.coupon_code.benifiters.all():
        paypal_dict  = {
            "cmd": "_xclick-subscriptions",
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            "a1": str(the_profile.coupon_code.trying_period_price),	# trial price
	        "p1": the_profile.coupon_code.trying_period, # trial duration of each unit (depends on unit)
            "t1": the_profile.coupon_code.duration_unite,  # duration unit ("M for Month"
            "a3": price,  # monthly price
            "p3": billing_cycle,  # duration of each unit (depends on unit)
            "t3": billing_cycle_unit,  # duration unit ("M for Month")
            "src": "1",  # make payments recur
            "sra": "1",  # reattempt payment on payment error
            "no_note": "1",  # remove extra notes (optional)
            'item_name': 'FB PUBLISHER',
            'custom': 1,     # custom data, pass something meaningful here
            "invoice": str(the_sub.id),
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                                            reverse('home:done')),
            'cancel_return': 'http://{}{}'.format(host,
                                                reverse('home:canceled')),
        }
    else:
        paypal_dict  = {
            "cmd": "_xclick-subscriptions",
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            "a3": price,  # monthly price
            "p3": billing_cycle,  # duration of each unit (depends on unit)
            "t3": billing_cycle_unit,  # duration unit ("M for Month")
            "src": "1",  # make payments recur
            "sra": "1",  # reattempt payment on payment error
            "no_note": "1",  # remove extra notes (optional)
            'item_name': 'FB PUBLISHER',
            'custom': 1,     # custom data, pass something meaningful here
            "invoice": str(the_sub.id),
            'currency_code': 'USD',
            'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                                            reverse('home:done')),
            'cancel_return': 'http://{}{}'.format(host,
                                                reverse('home:canceled')),
        }

    form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")
    return render(request, 'home/process_subscription.html', locals())


@login_required
@csrf_exempt
def payment_done(request):
    return render(request, 'home/payment_done.html')

@login_required
@csrf_exempt
def you_canceled_payment(request):
    return render(request, 'home/you_canceled_payment.html')


def settingsView(request):
    settings = settingModel2.objects.filter(user = request.user)

    context = {
        'settings':settings,
        'title':'settings'
        
    }

    return render(request, 'home/settings.html', context)

def clear_name(ele):
    new_ele = []
    for i in ele :
        if i in ["'","(",")",",","\\","\""]:
            pass
        else :
            new_ele.append(i)
    return ''.join(new_ele)

def editSettingsView(request):
    user = request.user
    my_profile = profile.objects.get(user=user)
    settings = settingModel2.objects.get(user = request.user)
    if request.method == 'POST':
        groups_per_time = int(clear_name(request.POST.get('groups_per_time')))
        posts_per_time = int(clear_name(request.POST.get('posts_per_time')))
        to_wait_after_each_join = int(clear_name(request.POST.get('to_wait_after_each_join')))
        to_wait_after_each_post = int(clear_name(request.POST.get('to_wait_after_each_post')))
        settings.group_join_per_time = groups_per_time
        settings.post_per_time = posts_per_time
        settings.to_wait_after_each_join = to_wait_after_each_join
        settings.to_wait_after_each_post = to_wait_after_each_post
        settings.save()

    context = {
        'title':'edit settings',
        'settings': settings,
        'my_profile': my_profile,
        'groups_per_time' : settings.group_join_per_time,
        'posts_per_time' : settings.post_per_time,
        'to_wait_after_each_join': settings.to_wait_after_each_join,
        'to_wait_after_each_post': settings.to_wait_after_each_post,
    }

    return render(request, 'home/edit_settings.html', context)

def same_pass(pass1, pass2):
    return pass1 == pass2


def prfileView(request):
    
    user = request.user
    my_profile = profile.objects.get(user=user)


    if request.method == 'POST' :
        first_name = request.POST.get("account-fn")
        last_name =  request.POST.get("account-ln")
        email = request.POST.get("account-email")
        username = request.POST.get("account-phone")
        password1 = request.POST.get("account-pass")
        password2 = request.POST.get("account-confirm-pass")
        print(clear_name(first_name))
        user.first_name = first_name,
        if password1 != '' and password2 != '' and same_pass(password1, password2) and len(password2) >= 8 :
                user.first_name = clear_name(first_name)
                user.last_name = clear_name(last_name)
                user.email = clear_name(email)
                user.username = clear_name(username)
                user.set_password(clear_name(password1))
                user.save()
        elif password1 == '' and password2 == '':
                user.first_name = clear_name(first_name)
                user.last_name = clear_name(last_name)
                user.email = clear_name(email)
                user.username = clear_name(username)
                user.save()
        else:
            messages.warning(request, 'the password are not the same or your password len is less than 8 chars')

    context = {
        'title':'profile',
        'user':user,
        'my_profile':my_profile,
        'first_name':clear_name(user.first_name),
        'last_name' : clear_name(user.last_name),
        'email' : clear_name(user.email),
        'username' : clear_name(user.username),
    }

    return render(request, 'home/profile.html', context)


def couponView(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        try:
            now = timezone.now()
            coupon = Coupon.objects.get(
                code = code,
                valid_to__gte = now,
                valid_from__lte  = now,
            )
            print('d')
            used_limits = coupon.number_of_used
            print('d2')
            if used_limits < coupon.number_of_used_limite:
                the_profile = profile.objects.get(user = request.user)
                if the_profile.coupon_code == coupon :
                    messages.warning(request, "you're already use this coupon")
                    return redirect('home:process_subscription')
                print('d3')
                the_profile.coupon_code = coupon
                the_profile.save()
                print('d4')
                coupon.number_of_used += 1
                coupon.save()
                print('d5')
                messages.success(request, 'this code was successfuly added ')
                return redirect('home:process_subscription')
            else:
                coupon.active = False
                coupon.save()
                messages.warning(request, 'this code was expired ')
                return redirect('home:process_subscription')
        except:
            messages.warning(request, 'this code is not exists or expaired ')
            return redirect('home:process_subscription')