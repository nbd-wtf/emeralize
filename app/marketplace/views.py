from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import json
from django.contrib import messages

from marketplace.models import *
from criticalpath.models import Journey, Resource, Category, Course, CourseResources, CoursePaymentSplits, Ebook
from django.contrib.auth.models import User

from .forms import UserProfileForm
from criticalpath.forms import ResourceForm


import requests, json, qrcode
import qrcode.image.svg
from io import BytesIO
from marketplace.config import API_KEY
from .util import *


# Create your views here.
def handle_not_found(request, exception):
    return render(request, 'emeralize/404.html')

def homepage(request):
    if request.user.is_authenticated:

        purchases = Purchase.objects.filter(user=request.user, resource=None)


        ctx = {
            'purchases' : purchases
        }

        return render(request, "emeralize/home.html", ctx)
     
    else:
        return render(request, "emeralize/home.html")

def terms(request):
    return render(request, "emeralize/terms.html")
def privacy(request):
    return render(request, "emeralize/privacy.html")

#List all resources
def discover(request):
    c = Category.objects.all()
    featured_creators_user_lists = FeaturedCreators.objects.all().order_by('sequence_number')
    creators = []
    for c in featured_creators_user_lists:
        creators.append(c.creator)
    featured_creators = UserProfile.objects.all().filter(user__in=creators)

    if request.user.is_authenticated:
    # need to add exclude already purchased resources.
        purchased_objects = Purchase.objects.filter(user=request.user)
        print(purchased_objects)
        # how to filter out the user created resources
        # free_resources = Resource.objects.all().filter(price=0).exclude(creator=request.user).exclude(id__in=purchased_objects)
        # paid_resources = Resource.objects.all().filter(price__gt=0).exclude(creator=request.user).exclude(id__in=purchased_objects)
        courses = FeaturedCourses.objects.all()
        ebooks = FeaturedEbooks.objects.all()
        workshops = FeaturedWorkshops.objects.all()


        ctx = {
            'ebooks' : ebooks,
            'courses' : courses,
            'featured_creators':featured_creators,
            'workshops':workshops

        }
    else:
        courses = FeaturedCourses.objects.all()
        ebooks = FeaturedEbooks.objects.all()
        workshops = FeaturedWorkshops.objects.all()


        ctx = {
            'ebooks' : ebooks,
            'courses' : courses,
            'workshops':workshops,
            'featured_creators':featured_creators
        }
    # j = Journey.objects.all().exclude(creator=request.user)



    
    print(ctx)
    return render(request, "marketplace/discover.html", ctx)

class ResourcePurchaseDetailView(View):
    model = Resource
    template_name = "marketplace/resource_detail.html"
    def get(self, request, pk) :
        purchase = False

        x = get_object_or_404(Resource, id=pk)

        if x.price == 0:
            return redirect(reverse('criticalpath:resource_detail', args=[x.id]))
        if request.user.is_authenticated:
            p = Purchase.objects.all().filter(resource=x, user=request.user)
            if p:
                purchase = True
        if x.status != 1:
            return redirect(reverse('marketplace:discover'))

        context = { 'resource' : x, 'purchased': purchase}
        return render(request, self.template_name, context)

class CoursePurchaseDetailView(View):
    model = Course
    template_name = "marketplace/course_detail.html"
    def get(self, request, pk) :
        purchase = False
        x = get_object_or_404(Course, id=pk)
        user_profile = UserProfile.objects.get(user=x.creator)
        course_resources = CourseResources.objects.filter(course=x).order_by('order_no')

        if x.price == 0:
            return redirect(reverse('criticalpath:course_detail', args=[x.id]))

        if request.user.is_authenticated:
            p = Purchase.objects.all().filter(course=x, user=request.user)

            if p:
                purchase = True

        context = { 'course' : x, 'course_resources' : course_resources, 'purchased': purchase, "user_profile": user_profile }
        return render(request, self.template_name, context)


@login_required
def resource_buy_view(request, pk):


    model = Resource
    x = get_object_or_404(Resource, id=pk)
    p = Purchase.objects.all().filter(user=request.user, resource=x)
    if p:
        messages.error(request, "You already own this resource.")

        resource_pk = x.id
        return redirect(reverse('criticalpath:resource_detail', args=[resource_pk]))
    if request.user.id == x.creator.id:
        messages.error(request, "You cannot purchase your own resource.")

        return redirect(reverse_lazy('criticalpath:my-creations'))


    ln_data = create_charge("resource_purchase", request.user, x.id, x.title, str(x.price) + "000")
    print(ln_data)
                        
    url = request.build_absolute_uri()
    context = { 'resource' : x, 'ln_invoice' : ln_data, 'url' : url}
    return render(request, "marketplace/buy.html", context)



class EbookPurchaseDetailView(View):
    model = Ebook
    template_name = "marketplace/ebook_detail.html"
    def get(self, request, pk) :
        purchase = False

        x = get_object_or_404(Ebook, id=pk)

        if x.price == 0:
            return redirect(reverse('criticalpath:ebook_detail', args=[x.id]))
        if request.user.is_authenticated:
            p = Purchase.objects.all().filter(ebook=x, user=request.user)
            if p:
                purchase = True
        if x.status != 1:
            return redirect(reverse('marketplace:discover'))

        context = { 'ebook' : x, 'purchased': purchase}
        return render(request, self.template_name, context)


@login_required
def ebook_buy_view(request, pk):


    model = Ebook
    x = get_object_or_404(Ebook, id=pk)

    p = Purchase.objects.all().filter(user=request.user, ebook=x)
    if p:
        messages.error(request, "You already own this ebook.")

        ebook_pk = x.id
        return redirect(reverse('criticalpath:ebook_detail', args=[ebook_pk]))
    if request.user.id == x.creator.id:
        messages.error(request, "You cannot purchase your own ebook.")

        return redirect(reverse_lazy('criticalpath:my-creations'))

    # create a function out of this once it works.
    msats_amount = get_msat_amount(x.price, x.currency_type.id)
    print(msats_amount)

    ln_data = create_charge("ebook_purchase", request.user, x.id, x.title, msats_amount)
    print(ln_data)

    url = request.build_absolute_uri()
    context = { 'ebook' : x, 'ln_invoice' : ln_data, 'url' : url}
    return render(request, "marketplace/ebook_buy.html", context)


@login_required
def ebook_success(request, ebook):
    x = Ebook.objects.get(id=ebook)
    context = {"ebook" : x}
    if request.method == 'GET':
        return render(request, "marketplace/ebook_success.html", context)

#Workshops
class WorkshopPurchaseDetailView(View):
    model = Workshop
    template_name = "marketplace/workshop/workshop_detail.html"
    def get(self, request, pk) :
        purchase = False

        x = get_object_or_404(Workshop, id=pk)

        if x.price == 0:
            return redirect(reverse('criticalpath:workshop_detail', args=[x.id]))
        if request.user.is_authenticated:
            p = Purchase.objects.all().filter(workshop=x, user=request.user)
            if p:
                purchase = True
        if x.status != 1:
            return redirect(reverse('marketplace:discover'))

        context = { 'workshop' : x, 'purchased': purchase}
        return render(request, self.template_name, context)


@login_required
def workshop_buy_view(request, pk):


    model = Workshop
    x = get_object_or_404(Workshop, id=pk)

    p = Purchase.objects.all().filter(user=request.user, workshop=x)
    if p:
        messages.error(request, "You already own this workshop.")

        workshop_pk = x.id
        return redirect(reverse('criticalpath:workshop_detail', args=[workshop_pk]))
    if request.user.id == x.creator.id:
        messages.error(request, "You cannot purchase your own workshop.")

        return redirect(reverse_lazy('criticalpath:my-creations'))

    # create a function out of this once it works.
    msats_amount = get_msat_amount(x.price, x.currency_type.id)
    print(msats_amount)

    ln_data = create_charge("workshop_purchase", request.user, x.id, x.title, msats_amount)
    print(ln_data)

    url = request.build_absolute_uri()
    context = { 'workshop' : x, 'ln_invoice' : ln_data, 'url' : url}
    return render(request, "marketplace/workshop/workshop_buy.html", context)


@login_required
def workshop_success(request, workshop):
    x = Workshop.objects.get(id=workshop)
    context = {"workshop" : x}
    if request.method == 'GET':
        return render(request, "marketplace/workshop/workshop_success.html", context)



@login_required
def course_buy_view(request, pk):


    model = Course
    x = get_object_or_404(Course, id=pk)
    p = Purchase.objects.all().filter(user=request.user, course=x)
    msats_amount = str(x.price) + "000"

    if p:
        messages.error(request, "You already own this course.")

        course_pk = x.id
        return redirect(reverse('criticalpath:course_detail', args=[course_pk]))
    if request.user.id == x.creator.id:
        request.session["error"] = "You cannot purchase your own course."
        messages.error(request, "You cannot purchase your own course.")

        return redirect(reverse_lazy('criticalpath:my-creations'))


    ln_data = create_charge("course_purchase", request.user, x.id, x.title, msats_amount)
    print(ln_data)
                        
    url = request.build_absolute_uri()
    context = { 'course' : x, 'ln_invoice' : ln_data, 'url' : url}
    return render(request, "marketplace/buy_course.html", context)


@login_required
def journey_buy_view(request, pk):
    model = Journey 
    x = Journey.objects.get(id=pk)

    URL = 'https://api.zebedee.io/v0/charges'
    heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    charge_data = json.dumps({
        "expiresIn": 600,
        "amount": x.price,
        "description": x.title,
        "internalId": f"journey:{x.id}",
        "callbackUrl": "https://emeralize.app/webhook/charge/"
    })



    response = requests.post(URL, headers=heads, data=charge_data).json()
    ln_data = response["data"]
    print(ln_data)
    #update with ln_data below:
    charge = Charge.objects.create(
                        user=request.user,
                        description=ln_data["description"],
                        amount=str(ln_data["amount"]) + "000",
                        status=ln_data["status"],
                        unit = "msats",
                        external_id=ln_data["id"],
                        internal_id=ln_data["internalId"],
                        callback_url=ln_data["callbackUrl"],
                        charge_encoded=ln_data["invoice"]["request"],
                        uri = ln_data["invoice"]["uri"],
                        expires_at=ln_data["expiresAt"],
                        created_at=ln_data["createdAt"]
                        ).save()

    context = { 'resource' : x, 'ln_invoice' : ln_data}
    return render(request, "marketplace/buy.html", context)

def zbd_webhook(request):
    webhook = json.loads(request.body)
    print(webhook)

    update_data = {
        "status": webhook["status"]
    }

    c = Charge.objects.filter(external_id=webhook["id"]).update(**update_data)
    c = Charge.objects.get(external_id=webhook["id"])

    if c.status == "completed":
        metadata = c.internal_id.split(":")
        charge_type = metadata[0]
        id = metadata[1]


        if "resource" in charge_type:
            resource = Resource.objects.get(id=int(id))
            # create purchase record for the user that purchased the resource.
            create_purchases(resource, c, "resource")

            # need to calc amount, min of 1 sat for a fee
            amount = resource.price
            payout_amount = calc_payout_amount(amount)
            # create transactions for resource owner
            execute_transactions(resource.creator, payout_amount, c, "resource", resource)

            # credit the resource owner for the payout amount
            execute_wallet_adjustments(resource.creator, payout_amount, c)   
            execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", resource.creator)

        elif "course" in charge_type:
            co = Course.objects.get(id=int(id))

            # create course purchase and course resource purchases
            create_purchases(co, c, "course")

            # get payment splitting config
            payment_splits = get_payment_split_config("course", co)

            # get payout_amount after fee
            payout_amount = calc_payout_amount(c.amount)

            # create transactions for course owner
            execute_transactions(co.creator, payout_amount, c, "course", co)

            # credit the course owner for the payout amount
            execute_wallet_adjustments(co.creator, payout_amount, c)

            if not payment_splits:
                # execute single payout
                execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", co.creator)

            else:
                # execute multiple payouts
                execute_payment_splits(payment_splits, payout_amount, co)

                # update the charge credit status to credited after everyone has received course balance credits. 
                update_credit_status(c)

                # execute payout for course owner
                print("executed owner payout for splits")
                execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", co.creator)
        elif "ebook" in charge_type:
            ebook = Ebook.objects.get(id=int(id))

           # create purchase record for the user that purchased the resource.
            create_purchases(ebook, c, "ebook")

            # get payment splitting config
            payment_splits = get_payment_split_config("ebook", ebook)

            # need to calc amount, min of 1 sat for a fee
            amount = get_sat_amount(ebook.price, ebook.currency_type.id)
            payout_amount = calc_payout_amount(amount)
            
            # create transactions for resource owner
            execute_transactions(ebook.creator, payout_amount, c, "ebook", ebook)

            # credit the ebook owner for the payout amount
            execute_wallet_adjustments(ebook.creator, payout_amount, c)
            if not payment_splits:
                # execute single payout
                execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", ebook.creator)

            else:
                # execute multiple payouts
                execute_payment_splits(payment_splits, payout_amount, ebook)

                # update the charge credit status to credited after everyone has received course balance credits. 
                update_credit_status(c)

                # execute payout for course owner
                print("executed owner payout for splits")
                execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", ebook.creator)
        elif "workshop" in charge_type:
            workshop = Workshop.objects.get(id=int(id))

           # create purchase record for the user that purchased the resource.
            create_purchases(workshop, c, "workshop")

            # get payment splitting config
            payment_splits = get_payment_split_config("workshop", workshop)

            # need to calc amount, min of 1 sat for a fee
            amount = get_sat_amount(workshop.price, workshop.currency_type.id)
            payout_amount = calc_payout_amount(amount)
            
            # create transactions for resource owner
            execute_transactions(workshop.creator, payout_amount, c, "workshop", workshop)

            # credit the ebook owner for the payout amount
            execute_wallet_adjustments(workshop.creator, payout_amount, c)
            if not payment_splits:
                # execute single payout
                execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", workshop.creator)

            else:
                # execute multiple payouts
                execute_payment_splits(payment_splits, payout_amount, workshop)

                # update the charge credit status to credited after everyone has received course balance credits. 
                update_credit_status(c)

                # execute payout for course owner
                print("executed owner payout for splits")
                execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", workshop.creator)

        elif "tip" in charge_type:
            creator = User.objects.get(id=int(id))
            # payout to creator
            # need to calc amount, min of 1 sat for a fee
            payout_amount = calc_payout_amount(c.amount)
            # create transactions for tip owner
            execute_transactions(creator, payout_amount, c, "tip", None)

            execute_wallet_adjustments(creator, payout_amount, c)   
            execute_single_payout("Automatic Withdrawal to Lightning Address from emeralize", creator)
        elif "withdrawal" in charge_type:
            pass
      

    return HttpResponse(True)

def tip_amount(request, username):
    user = get_object_or_404(User, username=username)
    if request.user.id == user.id:
        context = {"alert": "You cannot tip yourself."}
        return redirect(reverse_lazy('home'))
    creator = get_object_or_404(UserProfile, user=user)
    context = {'creator': creator}

    return render(request, "marketplace/tip_amount.html", context)

def tip_pay(request, username):
    creator = get_object_or_404(User, username=username)
    try:
        msat_amount = str(request.POST["amount"]) + "000"

        if request.user.id == creator.id:
            context = {"alert": "You cannot tip yourself."}
            return redirect(reverse_lazy('home'))
        
        creator_profile = get_object_or_404(UserProfile, user=creator)

        if request.user.is_authenticated:
            ln_data = create_charge("creator_tip", request.user, creator.id, f'Tip from {request.user} to {username}', msat_amount)
            print(ln_data)
        else:
            ln_data = create_charge("creator_tip", None, creator.id, f'Tip from Anonymous to {username}', msat_amount)
            print(ln_data)


        url = request.build_absolute_uri()

        context = { 'ln_invoice' : ln_data, 'creator_profile' : creator_profile, 'creator':creator, 'url' : url}
        return render(request, "marketplace/tip_pay.html", context)
    except:
        return redirect(reverse_lazy('marketplace:tip-amount', args=[username]))

def tip_success(request, username):
    context = {"status" : "Your tip was successful!" , 'creator' : username}
    return render(request, "marketplace/tip_success.html", context)

def charge_status_check(request):
    charge_id = request.GET["id"]
    origin = request.GET["origin"]

    c = Charge.objects.get(external_id=charge_id)
    if c.status == "completed":
        
        resp = HttpResponse("True")
        resp.headers["HX-Redirect"] = f'{origin}success'
        return resp

    else:
        return HttpResponse("Invoice has not been paid.")


@login_required
def resource_list(request):
    x = Resource.objects.all().exclude(creator=request.user.id)
    context = {"resources" : x}
    return render(request, "marketplace/resource_list.html", context)



@login_required
def resource_success(request, resource):
    x = Resource.objects.get(id=resource)
    context = {"resource" : x}
    if request.method == 'GET':
        return render(request, "marketplace/success.html", context)

@login_required
def course_success(request, course):
    x = Course.objects.get(id=course)
    y = get_object_or_404(Purchase, course=x, user=request.user)
    context = {"course" : x}
    if request.method == 'GET':
        return render(request, "marketplace/course_success.html", context)

@login_required
def journey_success(request, journey):
    x = Resource.objects.get(id=journey)
    context = {"resource" : x}
    if request.method == 'GET':
        return render(request, "marketplace/success.html", context)

@login_required
def purchase_history(request):
    user_owned_resources = Purchase.objects.filter(user=request.user)
    print(user_owned_resources[:2])
    context = {"purchases" : user_owned_resources[:4]}
    return render(request, "marketplace/purchase_history.html", context)

@login_required
def transaction_history(request):
    user_transactions = Transaction.objects.filter(user=request.user)

    context = {"user_transactions" : user_transactions}
    return render(request, "marketplace/transaction_history.html", context)

class UserProfileCreate(LoginRequiredMixin, View):
    template = 'marketplace/form.html'
    success_url = reverse_lazy('home')




    def get(self, request):
        page_header = "Profile Details"
        try:
            profile = request.user.user_profile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=request.user)

        form = UserProfileForm(instance=profile)
        ctx = {'form': form, "page_header" : page_header}
        return render(request, self.template, ctx)

    def post(self, request):
        try:
            profile = request.user.user_profile
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=request.user)

        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template, ctx)

        form.save()
        return redirect(self.success_url)

def profile(request, username):
    educator = get_object_or_404(User, username=username)
    educator_profile = get_object_or_404(UserProfile, user=educator)
    creator_resources = Resource.objects.filter(creator=educator, status=1)
    creator_courses = Course.objects.all().filter(creator=educator, status=1)
    creator_ebooks = Ebook.objects.all().filter(creator=educator, status=1)
    creator_workshops = Workshop.objects.all().filter(creator=educator, status=1)



    ctx = {'educator_profile': educator_profile, 'educator': educator,'creator_workshops': creator_workshops, 'creator_ebooks': creator_ebooks, 'creator_resources': creator_resources, 'creator_courses':creator_courses}
    return render(request, 'accounts/profile.html', ctx)

@login_required
def wallet_view(request):
    #example response
    # {'id': '9362eeca-0572-4f3e-996f-d43c8044f6f9', 'min_amt': 3, 'max_amt': 3, 'description': 'user withdrawal', 'callback_url': 'https://4c13-2600-8800-100-2dd0-00-ffc2.ngrok.io/webhook/withdrawal', 'uri': 'lightning:LNURL1DP68GURN8GHJ7CTSDYHX7UR9DEHX7ER99E3K7MF0WCEZ7MRWW4EXCTTHD96XSERJV9MKZMP0WFJKZEP08YENVVN9V43KZTFSX5MNYTF5VCEK2TFE8YMXVTTYXSEKXWPSXS6XVDNX8Y074MKK', 'lnurl': 'LNURL1DP68GURN8GHJ7CTSDYHX7UR9DEHX7ER99E3K7MF0WCEZ7MRWW4EXCTTHD96XSERJV9MKZMP0WFJKZEP08YENVVN9V43KZTFSX5MNYTF5VCEK2TFE8YMXVTTYXSEKXWPSXS6XVDNX8Y074MKK', 'created_at': '2021-12-27T02:55:32.655Z', 'expiry_date': '2022-12-27T02:55:32.652Z', 'used': False}
    user_wallet = Wallet.objects.get(user=request.user) 
    user_transactions = Transaction.objects.filter(user=request.user)

    # it will be beter for everyone to start w/ a lightning address and stops double spend.
    # if user_wallet.balance >= 10:
    #     try:
    #         w = Withdrawal.objects.filter(user=request.user).latest('created_at')
    #         if w:
    #             url = f'https://api.zebedee.io/v0/withdrawal-requests/{w.external_id}'
    #             heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    #             response = requests.get(url, headers=heads).json()
    #             update_data = {
    #                 "status": response["data"]["status"]
    #             }

    #             Withdrawal.objects.filter(external_id=response["data"]["id"]).update(**update_data)

    #             w = Withdrawal.objects.get(external_id=response["data"]["id"])
    #             if w.status == 'pending':
    #                 ctx = {
    #                     'user_wallet' : user_wallet,
    #                     "user_transactions" : user_transactions,
    #                     'withdrawal':  w
    #                 }
    #                 return render(request, "marketplace/wallet.html", ctx)


    #             elif w.status == 'expired' or w.status == 'completed':
    #                 URL = 'https://api.zebedee.io/v0/withdrawal-requests'
    #                 heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    #                 withdrawal_payload = json.dumps({
    #                     "expiresIn": 600,
    #                     "amount": str(user_wallet.balance) + "000",
    #                     "description": f"{request.user} withdrawal.",
    #                     "internalId": "",
    #                     "callbackUrl": "https://emeralize.app/webhook/withdrawal/"
    #                 })


    #                 response = requests.post(URL, headers=heads, data=withdrawal_payload).json()
    #                 ln_data = response["data"]
    #                 amount = int(int(ln_data["amount"]) / 1000)

    #                 Withdrawal.objects.create(
    #                     user=request.user,
    #                     description=ln_data["description"],
    #                     amount=amount,
    #                     status=ln_data["status"],
    #                     unit = "sats",
    #                     external_id=ln_data["id"],
    #                     internal_id=ln_data["internalId"],
    #                     callback_url=ln_data["callbackUrl"],
    #                     lnurl_withdrawal_encoded=ln_data["invoice"]["request"],
    #                     uri = ln_data["invoice"]["uri"],
    #                     expires_at=ln_data["expiresAt"],
    #                     created_at=ln_data["createdAt"]
    #                                     ).save()
    #                 w = Withdrawal.objects.get(external_id=response["data"]["id"])

    #                 ctx = {
    #                     'user_wallet' : user_wallet,
    #                     "user_transactions" : user_transactions,
    #                     'withdrawal':  w
    #                 }
    #                 return render(request, "marketplace/wallet.html", ctx)
    #         else:
    #             URL = 'https://api.zebedee.io/v0/withdrawal-requests'
    #             heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    #             withdrawal_payload = json.dumps({
    #                 "expiresIn": 600,
    #                 "amount": str(user_wallet.balance) + "000",
    #                 "description": f"{request.user} withdrawal.",
    #                 "internalId": "",
    #                 "callbackUrl": "https://emeralize.app/webhook/withdrawal/"
    #             })


    #             response = requests.post(URL, headers=heads, data=withdrawal_payload).json()
    #             ln_data = response["data"]
    #             amount = int(int(ln_data["amount"]) / 1000)

    #             Withdrawal.objects.create(
    #                 user=request.user,
    #                 description=ln_data["description"],
    #                 amount=amount,
    #                 status=ln_data["status"],
    #                 unit = "sats",
    #                 external_id=ln_data["id"],
    #                 internal_id=ln_data["internalId"],
    #                 callback_url=ln_data["callbackUrl"],
    #                 lnurl_withdrawal_encoded=ln_data["invoice"]["request"],
    #                 uri = ln_data["invoice"]["uri"],
    #                 expires_at=ln_data["expiresAt"],
    #                 created_at=ln_data["createdAt"]
    #                                 ).save()
    #             w = Withdrawal.objects.get(external_id=response["data"]["id"])

    #             ctx = {
    #                 'user_wallet' : user_wallet,
    #                 "user_transactions" : user_transactions,
    #                 'withdrawal':  w
    #             }
    #             return render(request, "marketplace/wallet.html", ctx)   
    #     except:
    #         URL = 'https://api.zebedee.io/v0/withdrawal-requests'
    #         heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
    #         withdrawal_payload = json.dumps({
    #             "expiresIn": 600,
    #             "amount": str(user_wallet.balance) + "000",
    #             "description": f"{request.user} withdrawal.",
    #             "internalId": "",
    #             "callbackUrl": "https://emeralize.app/webhook/withdrawal/"
    #         })


    #         response = requests.post(URL, headers=heads, data=withdrawal_payload).json()
    #         ln_data = response["data"]
    #         amount = int(int(ln_data["amount"]) / 1000)

    #         Withdrawal.objects.create(
    #             user=request.user,
    #             description=ln_data["description"],
    #             amount=amount,
    #             status=ln_data["status"],
    #             unit = "sats",
    #             external_id=ln_data["id"],
    #             internal_id=ln_data["internalId"],
    #             callback_url=ln_data["callbackUrl"],
    #             lnurl_withdrawal_encoded=ln_data["invoice"]["request"],
    #             uri = ln_data["invoice"]["uri"],
    #             expires_at=ln_data["expiresAt"],
    #             created_at=ln_data["createdAt"]
    #                             ).save()
    #         w = Withdrawal.objects.get(external_id=response["data"]["id"])

    #         ctx = {
    #             'user_wallet' : user_wallet,
    #             "user_transactions" : user_transactions,
    #             'withdrawal':  w
    #         }
    #         return render(request, "marketplace/wallet.html", ctx)
    withdrawal_eligible=False
    if user_wallet.balance >= 10:
        withdrawal_eligible=True


    ctx = {
        'user_wallet' : user_wallet,
        "user_transactions" : user_transactions,
        "withdrawal_eligible" : withdrawal_eligible
    }
    return render(request, "marketplace/wallet.html", ctx)

@login_required
def withdrawal(request):
    if request.method == 'GET':
        messages.success(request, ("Please only withdraw using the withdrawal button."))
        return redirect(reverse('marketplace:wallet'))    

    if request.method == 'POST':
        user_wallet = Wallet.objects.get(user=request.user) 
        user_profile = UserProfile.objects.get(user=request.user)
        update_lock_status = {"is_locked" : True}
        Wallet.objects.filter(user=request.user).update(**update_lock_status)
        if user_profile.lightning_address == None:
            messages.success(request, ("In order to withdraw, you need a lightning address. Please add one to your profile."))
            update_lock_status = {"is_locked" : False}
            Wallet.objects.filter(user=request.user).update(**update_lock_status)
            return redirect(reverse('marketplace:wallet'))    
        if user_wallet.balance >= 10:

            # check if ln address is valid
            url = f'https://api.zebedee.io/v0/ln-address/validate/{user_profile.lightning_address}'
            heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
            response = requests.get(url, headers=heads).json()
            # if it is a valid ln address
            if response["data"]["valid"]:

                URL = 'https://api.zebedee.io/v0/ln-address/send-payment'
                heads = {'Content-Type': 'application/json', 'apikey': API_KEY}
                lnadrs_payment_payload = json.dumps({
                    "lnAddress": f"{user_profile.lightning_address}",
                    "amount": f"{user_wallet.balance}" + "000",
                    "comment": "emeralize Withdrawal."
                })

                if not user_wallet.is_locked:
                    response = requests.post(URL, headers=heads, data=lnadrs_payment_payload).json()
                    if response["success"]:
                        t_code = TransactionCode.objects.get(transaction_code_text="Withdrawal")
                        # may worth be worth considering creating a withdrawal object with a status of in_flight even if payment is not a success to try and prevent double spend.
                        transaction = Transaction.objects.create(
                                            description=f"Withdrawal for {user_wallet.balance} to {user_profile.lightning_address} from emeralize",
                                            user=request.user,
                                            amount=user_wallet.balance,
                                            transaction_code=t_code
                                            ).save()
                        new_balance = 0
                        update_balance_data = {
                            "balance": new_balance,
                        }
                        Wallet.objects.filter(user=request.user).update(**update_balance_data)        

                        update_lock_status = {"is_locked" : False}
                        Wallet.objects.filter(user=request.user).update(**update_lock_status)
                        messages.success(request, ("Withdrawal successful."))
                        return redirect(reverse('marketplace:wallet'))    
                    else:
                        update_lock_status = {"is_locked" : False}
                        Wallet.objects.filter(user=request.user).update(**update_lock_status)
                        msg = response["message"]
                        messages.success(request, (f"Payment failed. {msg}"))
                        return redirect(reverse('marketplace:wallet'))    
                else:
                    messages.success(request, (f"Withdrawal already in process. Please wait before proceeding another withdrawal request."))
                    return redirect(reverse('marketplace:wallet'))                      
                # check if the payment was successful and update balance to 0 if it was

            else:
                update_lock_status = {"is_locked" : False}
                Wallet.objects.filter(user=request.user).update(**update_lock_status)
                msg = response["message"]
                messages.success(request, (f"Payment failed. {msg}"))
                return redirect(reverse('marketplace:wallet'))    
    
