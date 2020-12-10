from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from paypal.standard.models import ST_PP_COMPLETED
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from datetime import datetime
from .models import profile, subscription, Coupon
from django.shortcuts import get_object_or_404
from django.utils import timezone

def addMonthToStartDate():
    return timezone.now() + timezone.timedelta(days=33)

def addSixMonthToStartDate():
    return timezone.now() + timezone.timedelta(days=186)

def addYearToStartDate():
    return timezone.now() + timezone.timedelta(days=368)

@receiver(valid_ipn_received)
def ipn_receiver(sender, **kwargs):
    print('we are in signales')
    ipn_obj = sender
    print(f'ipn_obj {ipn_obj}')
    print(f'ipn_obj.invoce {ipn_obj.invoice}')
    print(f'ipn_obj.txn_type {ipn_obj.txn_type}')
    # check for Buy Now IPN
    if ipn_obj.txn_type == 'web_accept':
        print('great2222')
        if ipn_obj.payment_status == ST_PP_COMPLETED:
            # payment was successful
            print('great!')
            my_subscription = get_object_or_404(subscription, id=ipn_obj.invoice)
            my_profile = get_object_or_404(profile, profile_subscription=my_subscription)

            
            if my_profile.coupon_code:
                peroid = None
                coupon = my_profile.coupon_code
                if coupon.duration_unite == 'D':
                    peroid = timezone.now() + timezone.timedelta(days=coupon.trying_period)
                elif coupon.duration_unite == 'Y':
                    peroid = addYearToStartDate * coupon.trying_period
                else:
                    peroid = addMonthToStartDate * coupon.trying_period
                
                my_subscription.valid_to = my_subscription.valid_from + peroid
                my_subscription.save()

            if my_subscription.get_total_cost() == ipn_obj.mc_gross:
                # mark the order as paid
                my_subscription.paid = True
                my_subscription.save()
                my_profile.subscription_status = 'active'
                my_profile.save()

    # check for subscription signup IPN
    elif ipn_obj.txn_type == "subscr_signup":

        # get user id and activate the account
        sub_id = ipn_obj.invoice
        sub = subscription.objects.get(id=sub_id)
        sub_profile = get_object_or_404(profile, profile_subscription=sub)
        coupon = sub_profile.coupon_code

        if coupon:
            peroid = None
            coupon.benifiters.add(sub_profile.user)
            coupon.save()
            if coupon.duration_unite == 'D':
                peroid = timezone.now() + timezone.timedelta(days=coupon.trying_period)
            elif coupon.duration_unite == 'Y':
                peroid = addYearToStartDate * coupon.trying_period
            else:
                peroid = addMonthToStartDate * coupon.trying_period
            
            sub.valid_to = my_subscription.valid_from + peroid
            sub.save()

        user = sub_profile.user
        user.active = True
        user.save()
        sub.paid = True
        sub.save()
        sub_profile.subscription_status = 'active'
        sub_profile.save()

        subject = 'Sign Up Complete'

        message = 'Thanks for signing up!'

        email = EmailMessage(subject,
                             message,
                             'noreplay@fbpublisher.com',
                             [user.email])

        email.send()

    # check for subscription payment IPN
    elif ipn_obj.txn_type == "subscr_payment":



        # get user id and extend the subscription
        sub_id = ipn_obj.invoice
        sub = subscription.objects.get(id=sub_id)
        sub_profile = get_object_or_404(profile, profile_subscription=sub)
        user = sub_profile.user
        user.active = True
        user.save()
        sub.paid = True
        sub.save()
        sub_profile.subscription_status = 'active'
        sub_profile.save()

        coupon = sub_profile.coupon_code
        if coupon:
            peroid = None
            coupon.benifiters.add(sub_profile.user)
            coupon.save()
            if coupon.duration_unite == 'D':
                peroid = timezone.now() + timezone.timedelta(days=coupon.trying_period)
            elif coupon.duration_unite == 'Y':
                peroid = addYearToStartDate * coupon.trying_period
            else:
                peroid = addMonthToStartDate * coupon.trying_period
            
            sub.valid_to = my_subscription.valid_to + peroid
            sub.save()
            
        else:
            peroid = None
            if sub.subscription_duration == 's':
                peroid = addSixMonthToStartDate

            elif sub.subscription_duration == 'y':
                peroid = addYearToStartDate 

            else:
                peroid = addMonthToStartDate
            
            sub.valid_to = my_subscription.valid_to + peroid
            sub.save()
        

        # user.extend()  # extend the subscription

        subject = 'Your Invoice for {} is available'.format(
            datetime.strftime(datetime.now(), "%b %Y"))

        message = 'Thanks for using our service. The balance was automatically ' \
                  'charged to your credit card.'

        email = EmailMessage(subject,
                             message,
                             'noreplay@fbpublisher.com',
                             [user.email])

        email.send()

    # check for failed subscription payment IPN
    elif ipn_obj.txn_type == "subscr_failed":
        sub_id = ipn_obj.invoice
        sub = subscription.objects.get(id=sub_id)
        sub_profile = get_object_or_404(profile, profile_subscription=sub)
        user = sub_profile.user
        user.active = True
        user.save()
        sub.paid = False
        sub.save()
        sub_profile.subscription_status = 'unactive'
        sub_profile.save()

        subject = 'You Canceled Your Subscription'
        message = f"""
        Hello {user.username}

        We couldn't process your payment for this month.
        It looks like your card is being declined.
        To resolve, the issue we suggest you to check your payment info.
        You may also need to contact the bank to get more information on the issue.

        Happy to help.

        Customer Support

        """

        email = EmailMessage(subject,
                             message,
                             'noreplay@fbpublisher.com',
                             [user.email])

        email.send()

    # check for subscription cancellation IPN
    elif ipn_obj.txn_type == "subscr_cancel":
        sub_id = ipn_obj.invoice
        sub = subscription.objects.get(id=sub_id)
        sub_profile = get_object_or_404(profile, profile_subscription=sub)
        user = sub_profile.user
        user.active = True
        user.save()
        sub.paid = False
        sub.save()
        sub_profile.subscription_status = 'unactive'
        sub_profile.save()

        subject = 'You Canceled Your Subscription'

        message = 'Thanks for using our service. You Canceled Your Subscription.'

        email = EmailMessage(subject,
                             message,
                             'noreplay@fbpublisher.com',
                             [user.email])

        email.send()


