from django.contrib import messages
from criticalpath.models import *
from criticalpath.owner import OwnerListView, OwnerDetailView, OwnerCreateView, OwnerUpdateView, OwnerDeleteView

from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.core.files.uploadedfile import InMemoryUploadedFile
from criticalpath.forms import *
from django.contrib.humanize.templatetags.humanize import naturaltime
from marketplace.models import Purchase, Wallet, Transaction, TransactionCode, UserProfile, FeaturedCourses

from criticalpath.utils import dump_queries
from django.db.models import Q, Max
from django.core.files.storage import FileSystemStorage


@login_required
def creation_list(request):
    if request.POST:
        if request.POST["agree"]:
            update_data = {
                "creator": True,
            }
            UserProfile.objects.filter(user=request.user).update(**update_data)
            
            context = {"courses" : c , "resources" : r, "creator_profile":creator_profile}
            return render(request, "criticalpath/creator.html")
        else:
            form = CreatorSignUpForm()
            context = {"form" : form}

            return render(request, "criticalpath/creator.html", context)
    else:
        creator_profile = get_object_or_404(UserProfile, user=request.user)
        if creator_profile.creator:
            c = Course.objects.filter(creator=request.user)
            r = Resource.objects.filter(creator=request.user)
            e = Ebook.objects.filter(creator=request.user)
            w = Workshop.objects.filter(creator=request.user)


            context = {"courses" : c , "resources" : r, 'ebooks' :e, "workshops" : w, "creator_profile":creator_profile}
            return render(request, "criticalpath/creator.html", context)

        else:
            form = CreatorSignUpForm()
            context = {"form" : form}

            return render(request, "criticalpath/creator.html", context)
 


@login_required
def journey_list(request):
    j = Journey.objects.all().exclude(creator=request.user)
    context = {"journeys" : j}
    return render(request, "marketplace/journey_list.html", context)


class UserCriticalPathDetailView(OwnerListView):
    model = Journey
    template_name = "criticalpath/my_critical_path.html"

    def get(self, request) :
        journey_list = Journey.objects.filter(creator=self.request.user)


        ctx = {'journey_list' : journey_list}

        return render(request, self.template_name, ctx)

class CriticalPathDetailView(OwnerListView):
    model = Journey
    template_name = "criticalpath/list.html"

    def get(self, request) :
        journey_list = Journey.objects.all().exclude(creator=request.user.id)
        ctx = {'journey_list' : journey_list}
        return render(request, self.template_name, ctx)

class JourneyDetailView(OwnerDetailView):
    model = Journey
    template_name =  "criticalpath/detail.html"
    def get(self, request, pk) :
        j = Journey.objects.get(id=pk)
        comments = Comment.objects.filter(journey=j).order_by('-last_modified_at')
        comment_form = CommentForm()
        # phases = Phase.objects.filter(journey=j).order_by('phase_number')
        resources = JourneyResources.objects.filter(journey=j)
        # context = { 'journey' : j, "phases" : phases, 'resources' : resources, 'comments': comments, 'comment_form': comment_form }
        context = { 'journey' : j, 'resources' : resources, 'comments': comments, 'comment_form': comment_form }

        return render(request, self.template_name, context)

class JourneyCreateView(OwnerCreateView):

    template_name =  "criticalpath/form.html"
    #update release with phase when ready
    # success_url = reverse_lazy('criticalpath:phase_create')
    def get(self, request, pk=None) :
        header_name = 'Create a Journey'
        form = JourneyForm()
        ctx = { 'form' : form, 'header_name' : header_name }
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        form = JourneyForm(self.request.POST)

        if not form.is_valid():
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        # Add creator to the model before saving

        journey = form.save(commit=False)
        journey.creator = request.user
        journey.save()
        journey_pk = journey.id
        return redirect(reverse('criticalpath:resource_add', args=[journey_pk]))

class JourneyUpdateView(OwnerUpdateView):
    template_name =  "criticalpath/form.html"
    header_name = "Update Journey"
    def get(self, request, pk) :
        journey = get_object_or_404(Journey, id=pk, creator=self.request.user)
        form = JourneyForm(instance=journey)
        ctx = { 'form': form }
        return render(request, self.template_name, ctx)

    def post(self, request, pk=None) :
        journey = get_object_or_404(Journey, id=pk, creator=self.request.user)
        form = JourneyForm(request.POST, request.FILES or None, instance=journey)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        journey = form.save(commit=False)
        journey.save()

        return redirect(reverse('criticalpath:journey_detail', args=[pk]))

class JourneyDeleteView(OwnerDeleteView):
    model = Journey
    template_name = "criticalpath/confirm_delete.html"


# class PhaseDetailView(OwnerDetailView):
#     model = Phase
#     template_name =  "criticalpath/phase_detail.html"
#     def get(self, request, pk, phase_pk) :
#         j = Journey.objects.get(id=pk)
#         p = Phase.objects.get(id=phase_pk)
#         r = Resource.objects.filter(phase=p)
#         context = { 'journey': j,  'phase' : p, 'resources' : r }
#         return render(request, self.template_name, context)

# class PhaseCreateView(OwnerCreateView):
#     template_name =  "criticalpath/form.html"
#     def get(self, request, pk) :
#         form = PhaseForm()
#         ctx = { 'form' : form, 'header_name' : 'Create a Phase' }
#         return render(request, self.template_name, ctx)

#     def post(self, request, pk) :
#         form = PhaseForm(request.POST)

#         if not form.is_valid() :
#             ctx = {'form' : form}
#             return render(request, self.template_name, ctx)

#         # Add creator to the model before saving
#         journey = Journey.objects.get(id=pk)
#         phase = form.save(commit=False)
#         phases = Phase.objects.filter(journey=pk)
#         highest_phase = 0
#         for p in phases:
#             if p.phase_number > highest_phase:
#                 highest_phase = p.phase_number
#         highest_phase = highest_phase + 1
#         phase.phase_number = highest_phase
#         phase.journey = journey
#         phase.save()
#         journey_pk = journey.id
#         phase_pk = phase.id
#         return redirect(reverse('criticalpath:resource_create', args=[journey_pk, phase_pk]))
class CourseDetailView(OwnerDetailView):
    model = Course
    template_name =  "criticalpath/course_detail.html"
    def get(self, request, course_pk) :
        c = get_object_or_404(Course, id=course_pk)
        if request.user.is_authenticated:
            p = Purchase.objects.all().filter(course=c, user=request.user)
            if c.creator == request.user or p or c.price == 0:
                c_resources = CourseResources.objects.filter(course=c).order_by('order_no')
                context = { 'course' : c, 'course_resources' : c_resources}

                return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first purchase this course.")

                return redirect(reverse('marketplace:course_purchase_detail', args=[c.id]))
        else:
            if c.price == 0:
                    c_resources = CourseResources.objects.filter(course=c).order_by('order_no')
                    context = { 'course' : c, 'course_resources' : c_resources}
                    return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first login.")

                return redirect(reverse('signin'))


class CourseCreateView(OwnerCreateView):

    template_name =  "criticalpath/courses/form.html"
    #update release with phase when ready
    # success_url = reverse_lazy('criticalpath:phase_create')
    def get(self, request) :
        header_name = 'Create a Course'
        form = CourseForm()
        ctx = { 'form' : form, 'header_name' : header_name }
        return render(request, self.template_name, ctx)

    def post(self, request) :
        form = CourseForm(self.request.POST)
        request.POST

        if not form.is_valid():
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        # Add creator to the model before saving

        course = form.save(commit=False)
        course.creator = request.user
        course.save()
        course_pk = course.id
        return redirect(reverse('criticalpath:course_add_splits', args=[course_pk]))

class CourseAddResourcesView(OwnerCreateView):

    template_name =  "criticalpath/courses/add_resources_form.html"
    #update release with phase when ready
    # success_url = reverse_lazy('criticalpath:phase_create')
    def get(self, request, course_pk) :
        header_name = 'Add Resources to a Course'
        course = get_object_or_404(Course, id=course_pk, creator=request.user)
        resources = Resource.objects.filter(creator=request.user)
        
        try:
            course_resources = CourseResources.objects.filter(course=course).order_by('order_no')
            form = CourseAddResourcesForm(instance=course_resources)
        except:
            form = CourseAddResourcesForm()
        ctx = { 'form' : form, 'header_name' : header_name, 'course':course, 'course_resources': course_resources, 'resources': resources}
        return render(request, self.template_name, ctx)

    def post(self, request, course_pk) :
        # form = CourseAddResourcesForm(self.request.POST)

        # if not form.is_valid():
        #     ctx = {'form' : form}
        #     return render(request, self.template_name, ctx)

        # Add creator to the model before saving
        # course_form = form.save(commit=False)
        # course = Course.objects.get(id=course_pk)
        # course_form.course = course
        # course_form.save()
        c = Course.objects.get(id=course_pk)
        if request.user == c.creator:
            payload = request.POST.dict()
            print(payload)
            
            course_resources = []
            # index 0 = resource_id, index 1 = sequence_number
            resource = []
            for sequence_number, resource_id in payload.items():
                if 'csrf' not in sequence_number:
                    print("sequence_number:", sequence_number)

                    if int(sequence_number): 

                        print("resource id: ", resource_id)
                        r = Resource.objects.get(id=resource_id)
                        print(r.title)
                        print("sequence number: ", sequence_number)
                        resource.append(resource_id)
                        resource.append(sequence_number)
                        course_resources.append(resource)
                        resource = []



            # drop resources associated with course id and creator id
            CourseResources.objects.all().filter(course=c).delete()

            #insert new course data
            print(course_resources)
            for resource in course_resources:
                print("resource: ", resource)
                resource_pk = int(resource[0])
                seq_num = int(resource[1])
                r = Resource.objects.get(id=resource_pk)
                cr = CourseResources.objects.create(course=c, resource=r, order_no=seq_num)

            # ctx = {
            #     "course_resources" : course_resources
            # }
            messages.success(request, ("Nice work! Course details below."))

            return redirect(reverse('criticalpath:course_detail', args=[course_pk]))
        else:
            return redirect(reverse(['home']))

class CoursePaymentSplitsView(OwnerCreateView):

    template_name =  "criticalpath/courses/payment_splits.html"
    #update release with phase when ready
    # success_url = reverse_lazy('criticalpath:phase_create')
    def get(self, request, course_pk) :
        course = get_object_or_404(Course, id=course_pk, creator=request.user)
        creators = UserProfile.objects.all().filter(creator=True).exclude(user=request.user)
        
        try:
            course_payment_splits = CoursePaymentSplits.objects.filter(course=course)
            creator_share = 100
            for course_payment_split in course_payment_splits:
                creator_share -= course_payment_split.amount


            form = CoursePaymentSplitsForm(instance=course_payment_splits)
        except:
            form = CoursePaymentSplitsForm()
        ctx = { 'form' : form, 'course':course, 'course_payment_splits': course_payment_splits, 'creators': creators, 'creator_share':creator_share}
        return render(request, self.template_name, ctx)

    def post(self, request, course_pk) :
        # form = CourseAddResourcesForm(self.request.POST)

        # if not form.is_valid():
        #     ctx = {'form' : form}
        #     return render(request, self.template_name, ctx)

        # Add creator to the model before saving
        # course_form = form.save(commit=False)
        # course = Course.objects.get(id=course_pk)
        # course_form.course = course
        # course_form.save()
        c = Course.objects.get(id=course_pk)
        if request.user == c.creator:

            payload = request.POST.dict()
            
            users = []
            payout = []
            for key, value in payload.items():
                if 'csrf' not in key and 'owner' not in key:
                    # if int(key[-1]): 
                    payout.append(value)
                    if 'amount' in key:
                        users.append(payout)
                        payout = []


            print("top-level payment splits: ", users)

            # drop resources associated with course id and creator id
            CoursePaymentSplits.objects.all().filter(course=c).delete()

            #insert new course data
            total_percentage_amount = 0

            for split in users:
                amount = int(split[1])
                total_percentage_amount += amount
                if total_percentage_amount >= 100:
                    messages.error(request, "Please ensure that all of the amounts total to less than or equal to 100.")
                    creators = UserProfile.objects.all().filter(creator=True).exclude(user=request.user)
                    try:
                        course_payment_splits = CoursePaymentSplits.objects.filter(course=c)
                        form = CoursePaymentSplitsForm(instance=course_payment_splits)
                    except:
                        form = CoursePaymentSplitsForm()
                    ctx = { 'form' : form, 'course':c, 'course_payment_splits': course_payment_splits, 'creators': creators}
                    return render(request, self.template_name, ctx)

            for split in users:
                print(split)
                creator = User.objects.get(id=int(split[0]))
                amt = int(split[1])
                print("coure", c, "creator", creator, "amount", amt)
                cr = CoursePaymentSplits.objects.create(course=c, user=creator, amount=amt).save()
                print(cr)


            return redirect(reverse('criticalpath:course_add_resources', args=[course_pk]))
        else:
            return redirect(reverse(['home']))


class CourseUpdateView(OwnerUpdateView):
    template_name =  "criticalpath/courses/update_form.html"
    
    model = Course
    def get(self, request, course_pk) :
        course = get_object_or_404(Course, id=course_pk, creator=self.request.user)
        form = CourseForm(instance=course)
        header_name = "Update Course"
        ctx = { 'form': form, 'header_name':header_name, 'course': course}
        return render(request, self.template_name, ctx)

    def post(self, request, course_pk) :
        course = get_object_or_404(Course, id=course_pk, creator=self.request.user)
        form = CourseForm(request.POST, request.FILES or None, instance=course)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        course = form.save(commit=False)
        course.save()

        return redirect(reverse('criticalpath:course_add_splits', args=[course_pk]))

class CourseDeleteView(OwnerDeleteView):
    model = Course
    template_name = "criticalpath/confirm_delete.html"
    def get(self, request, course_pk) :
        course = get_object_or_404(Course, id=course_pk, creator=self.request.user)
        ctx = { 'course' : course }
        return render(request, self.template_name, ctx)
    def post(self, request, course_pk):
        course = get_object_or_404(Course, id=course_pk, creator=self.request.user)
        #consider moving to an archive status instead of deleting.
        course.delete()
        return redirect(reverse('criticalpath:my-creations'))



class CourseResourceDetailView(OwnerDetailView):
    model = Course
    template_name =  "criticalpath/resource_detail.html"
    def get(self, request, course_pk, resource_pk) :
        c = get_object_or_404(Course, id=course_pk)
        resource_sequence = CourseResources.objects.get(course=course_pk, resource=resource_pk)
        max_sequence_number = CourseResources.objects.all().filter(course=course_pk).aggregate(Max('order_no'))

        prev_back_to_course = False
        next_back_to_course = False


        if resource_sequence.order_no == max_sequence_number["order_no__max"]:
            next_back_to_course = True
            next_resource_sequence = False
            next_resource = False
        else:
            next_resource_sequence = resource_sequence.order_no + 1
            next_course_resource = CourseResources.objects.get(course=course_pk, order_no=next_resource_sequence)
            next_resource = Resource.objects.get(id=next_course_resource.resource.id)

        if resource_sequence.order_no == 1:
            prev_back_to_course = True
            prev_resource_sequence = False
            prev_resource = False
        else:
            prev_resource_sequence = resource_sequence.order_no - 1
            prev_course_resource = CourseResources.objects.get(course=course_pk, order_no=prev_resource_sequence)
            prev_resource = Resource.objects.get(id=prev_course_resource.resource.id)

        # p = Phase.objects.get(id=phase_pk)
        if request.user.is_authenticated:
            r = get_object_or_404(Resource, id=resource_pk)
            p = Purchase.objects.all().filter(resource=r, user=request.user)
            if r.creator == request.user or p or r.price == 0:

                context = { 'resource' : r, 'course' : c,
                "prev_resource_sequence": prev_resource_sequence, "prev_resource": prev_resource,"prev_back_to_course": prev_back_to_course,
                'resource_sequence' : resource_sequence, "max_sequence_number":max_sequence_number, "next_resource_sequence": next_resource_sequence, "next_resource": next_resource,"next_back_to_course": next_back_to_course 
                }
                reward = Reward.objects.all().filter(resource=r, user=request.user)
                if reward:
                    context["rewardRedeemed"] = True
                return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first purchase this resource.")
                return redirect(reverse('marketplace:resource_purchase_detail', args=[r.id]))
        else:
            r = get_object_or_404(Resource, id=resource_pk)
            if r.price == 0:
                    context = { 'resource' : r, 'course' : c,
                    "prev_resource_sequence": prev_resource_sequence, "prev_resource": prev_resource,"prev_back_to_course": prev_back_to_course,
                    'resource_sequence' : resource_sequence, "max_sequence_number":max_sequence_number, "next_resource_sequence": next_resource_sequence, "next_resource": next_resource,"next_back_to_course": next_back_to_course 
                    }
                    return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first login.")
                return redirect(reverse('signin'))

class ResourceDetailView(OwnerDetailView):
    model = Resource
    template_name =  "criticalpath/resource_detail.html"
    def get(self, request, resource_pk) :
        # p = Phase.objects.get(id=phase_pk)
        if request.user.is_authenticated:
            r = get_object_or_404(Resource, id=resource_pk)
            p = Purchase.objects.all().filter(resource=r, user=request.user)
            if r.creator == request.user or p or r.price == 0:
                context = { 'resource' : r }
                # reward = Reward.objects.all().filter(resource=r, user=request.user)
                # if reward:
                #     context["rewardRedeemed"] = True
                return render(request, self.template_name, context)

            else:
                messages.error(request, "You must first purchase this resource.")
                return redirect(reverse('marketplace:resource_purchase_detail', args=[r.id]))
        else:
            r = get_object_or_404(Resource, id=resource_pk)
            if r.price == 0:
                    context = { 'resource' : r}
                    return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first login.")
                return redirect(reverse('signin'))

#Resources
class ResourceCreateView(OwnerCreateView):
    template_name =  "criticalpath/form.html"
    def get(self, request) :
        if request.user.is_superuser:
            form = SuperResourceForm()

        else:
            form = ResourceForm()
        ctx = { 'form' : form, 'header_name' : 'Create a Resource' }
        return render(request, self.template_name, ctx)

    def post(self, request) :
        if request.user.is_superuser:
            form = SuperResourceForm(request.POST, request.FILES)
        else:
            form = ResourceForm(request.POST, request.FILES)
        # phase = Phase.objects.get(id=phase_pk)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)


        # Add creator to the model before saving
        resource = form.save(commit=False)
        resource.creator = request.user

        # resource.phase = phase
        resource.save()
        return redirect(reverse('criticalpath:resource_detail', args=[resource.id]))

class ResourceAddView(OwnerCreateView):
    template_name =  "criticalpath/form.html"
    def get(self, request, journey_pk) :
        form = AddResourceForm()
        ctx = { 'form' : form, 'header_name' : 'Add a Resource', 'resource_create' : True }
        return render(request, self.template_name, ctx)

    def post(self, request, journey_pk) :
        form = AddResourceForm(request.POST)
        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        journey_resource = form.save(commit=False)
        journey_resource.journey = Journey.objects.get(id=journey_pk)
        journey_resource.save()
        return redirect(reverse('criticalpath:journey_detail', args=[journey_pk]))

class ResourceUpdateView(OwnerUpdateView):
    template_name =  "criticalpath/form.html"
    def get(self, request, resource_pk) :
        resource = get_object_or_404(Resource, id=resource_pk, creator=self.request.user)
        if request.user.is_superuser:
            form = SuperResourceForm(instance=resource)
        else:
            form = ResourceForm(instance=resource)
        ctx = { 'form': form, "header_name": "Update Resource", "resource" : resource }
        return render(request, self.template_name, ctx)

    def post(self, request, resource_pk) :
        resource = get_object_or_404(Resource, id=resource_pk, creator=self.request.user)
        if request.user.is_superuser:
            form = SuperResourceForm(request.POST, request.FILES or None, instance=resource)
        else:
            form = ResourceForm(request.POST, request.FILES or None, instance=resource)


        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        resource = form.save(commit=False)
        resource.save()

        return redirect(reverse('criticalpath:resource_detail', args=[resource.id]))

class ResourceDeleteView(OwnerDeleteView):
    model = Resource
    template_name = "criticalpath/confirm_delete.html"
    def get(self, request, resource_pk) :
        resource = get_object_or_404(Resource, id=resource_pk, creator=self.request.user)
        ctx = { 'resource' : resource }
        return render(request, self.template_name, ctx)
    def post(self, request, resource_pk):
        resource = get_object_or_404(Resource, id=resource_pk, creator=self.request.user)
        # consider moving to an archive status instead of deleting.
        # exclude archive view from creator but still allow it to be viewed as a part of courses
        # allow existing purchased users to still view the content
        # disclude discovery from marketplace though by excluding any archived courses
        resource.delete()
        return redirect(reverse('criticalpath:my-creations'))

#Workshops
class WorkshopCreateView(OwnerCreateView):
    template_name =  "criticalpath/workshop/workshop_form.html"
    def get(self, request) :

        form = WorkshopForm()
        ctx = { 'form' : form, 'header_name' : 'Create an Workshop' }
        return render(request, self.template_name, ctx)

    def post(self, request) :

        form = WorkshopForm(request.POST, request.FILES)
        # phase = Phase.objects.get(id=phase_pk)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

   
        # Add creator to the model before saving
        workshop = form.save(commit=False)

        if workshop.price >= 250000 and workshop.currency_type.iso_code == "SAT":
            messages.error(request, "Price cannot be greater than 250,000 sats")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)        
        elif workshop.price > 25 and workshop.currency_type.iso_code == "USD":
            messages.error(request, "Price cannot be greater than $25.")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)       
        workshop.creator = request.user
        # resource.phase = phase
        workshop.save()
        return redirect(reverse('criticalpath:workshop_add_splits', args=[workshop.id]))

class WorkshopPaymentSplitsView(OwnerCreateView):

    template_name =  "criticalpath/workshop/workshop_payment_splits.html"
    #update release with phase when ready
    # success_url = reverse_lazy('criticalpath:phase_create')
    def get(self, request, workshop_pk) :
        workshop = get_object_or_404(Workshop, id=workshop_pk, creator=request.user)
        creators = UserProfile.objects.all().filter(creator=True).exclude(user=request.user)
        
        try:
            payment_splits = WorkshopPaymentSplits.objects.filter(workshop=workshop)
            creator_share = 100
            for payment_split in payment_splits:
                creator_share -= payment_split.amount


            form = WorkshopPaymentSplitsForm(instance=payment_splits)
        except:
            form = WorkshopPaymentSplitsForm()
        ctx = { 'form' : form, 'workshop':workshop, 'payment_splits': payment_splits, 'creators': creators, 'creator_share':creator_share}
        return render(request, self.template_name, ctx)

    def post(self, request, workshop_pk) :
        # form = CourseAddResourcesForm(self.request.POST)

        # if not form.is_valid():
        #     ctx = {'form' : form}
        #     return render(request, self.template_name, ctx)

        # Add creator to the model before saving
        # course_form = form.save(commit=False)
        # course = Course.objects.get(id=course_pk)
        # course_form.course = course
        # course_form.save()
        w = Workshop.objects.get(id=workshop_pk)
        if request.user == w.creator:

            payload = request.POST.dict()
            
            users = []
            payout = []
            for key, value in payload.items():
                if 'csrf' not in key and 'owner' not in key:
                    # if int(key[-1]): 
                    payout.append(value)
                    if 'amount' in key:
                        users.append(payout)
                        payout = []


            print("top-level payment splits: ", users)

            # drop resources associated with course id and creator id
            WorkshopPaymentSplits.objects.all().filter(workshop=w).delete()

            #insert new course data
            total_percentage_amount = 0

            for split in users:
                amount = int(split[1])
                total_percentage_amount += amount
                if total_percentage_amount >= 100:
                    messages.error(request, "Please ensure that all of the amounts total to less than or equal to 100.")
                    creators = UserProfile.objects.all().filter(creator=True).exclude(user=request.user)
                    try:
                        workshop_payment_splits = WorkshopPaymentSplits.objects.filter(workshop=w)
                        form = WorkshopPaymentSplitsForm(instance=workshop_payment_splits)
                    except:
                        form = WorkshopPaymentSplitsForm()
                    ctx = { 'form' : form, 'workshop':w, 'payment_splits': workshop_payment_splits, 'creators': creators}
                    return render(request, self.template_name, ctx)

            for split in users:
                print(split)
                creator = User.objects.get(id=int(split[0]))
                amt = int(split[1])
                print("workshop", w, "creator", creator, "amount", amt)
                workshop_splits = WorkshopPaymentSplits.objects.create(workshop=w, user=creator, amount=amt).save()


            return redirect(reverse('criticalpath:workshop_detail', args=[workshop_pk]))
        else:
            return redirect(reverse(['home']))

class WorkshopDetailView(OwnerDetailView):
    model = Workshop
    template_name =  "criticalpath/workshop/workshop_detail.html"
    def get(self, request, workshop_pk) :
        # p = Phase.objects.get(id=phase_pk)
        if request.user.is_authenticated:
            w = get_object_or_404(Workshop, id=workshop_pk)
            p = Purchase.objects.all().filter(workshop=w, user=request.user)
            if w.creator == request.user or p or w.price == 0:
                context = { 'workshop' : w }
                return render(request, self.template_name, context)

            else:
                messages.error(request, "You must first purchase this workshop.")
                return redirect(reverse('marketplace:workshop_purchase_detail', args=[w.id]))
        else:
            w = get_object_or_404(Workshop, id=workshop_pk)
            if w.price == 0:
                    context = { 'workshop' : w}
                    return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first login.")
                return redirect(reverse('signin'))

class WorkshopUpdateView(OwnerUpdateView):
    template_name =  "criticalpath/workshop/workshop_form.html"
    def get(self, request, workshop_pk) :
        workshop = get_object_or_404(Workshop, id=workshop_pk, creator=self.request.user)

        form = WorkshopForm(instance=workshop)
        ctx = { 'form': form, "header_name": "Update Workshop", "workshop" : workshop }
        return render(request, self.template_name, ctx)

    def post(self, request, workshop_pk) :
        workshop = get_object_or_404(Workshop, id=workshop_pk, creator=self.request.user)

        form = WorkshopForm(request.POST, request.FILES or None, instance=workshop)


        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        workshop = form.save(commit=False)

        if workshop.price >= 250000 and workshop.currency_type.iso_code == "SAT":
            messages.error(request, "Price cannot be greater than 250,000 sats")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)        
        elif workshop.price > 25 and workshop.currency_type.iso_code == "USD":
            messages.error(request, "Price cannot be greater than $25.")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)       
        workshop.save()

        return redirect(reverse('criticalpath:workshop_add_splits', args=[workshop.id]))

class WorkshopDeleteView(OwnerDeleteView):
    model = Workshop
    template_name = "criticalpath/workshop/workshop_confirm_delete.html"
    def get(self, request, workshop_pk) :
        workshop = get_object_or_404(Workshop, id=workshop_pk, creator=self.request.user)
        ctx = { 'workshop' : workshop }
        return render(request, self.template_name, ctx)
    def post(self, request, workshop_pk):
        workshop = get_object_or_404(Workshop, id=workshop_pk, creator=self.request.user)
        # consider moving to an archive status instead of deleting.
        # exclude archive view from creator but still allow it to be viewed as a part of courses
        # allow existing purchased users to still view the content
        # disclude discovery from marketplace though by excluding any archived courses
        workshop.delete()
        return redirect(reverse('criticalpath:my-creations'))



# Ebooks
class EbookCreateView(OwnerCreateView):
    template_name =  "criticalpath/ebook_form.html"
    def get(self, request) :

        form = EbookForm()
        ctx = { 'form' : form, 'header_name' : 'Create an Ebook' }
        return render(request, self.template_name, ctx)

    def post(self, request) :

        form = EbookForm(request.POST, request.FILES)
        # phase = Phase.objects.get(id=phase_pk)

        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

   
        # Add creator to the model before saving
        ebook = form.save(commit=False)
        print(ebook)
        print(ebook.price, ebook.currency_type.iso_code)
        if ebook.price >= 250000 and ebook.currency_type.iso_code == "SAT":
            messages.error(request, "Price cannot be greater than 250,000 sats")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)        
        elif ebook.price > 25 and ebook.currency_type.iso_code == "USD":
            messages.error(request, "Price cannot be greater than $25.")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)       
        ebook.creator = request.user
        # resource.phase = phase
        ebook.save()
        return redirect(reverse('criticalpath:ebook_add_splits', args=[ebook.id]))

class EbookPaymentSplitsView(OwnerCreateView):

    template_name =  "criticalpath/ebook_payment_splits.html"
    #update release with phase when ready
    # success_url = reverse_lazy('criticalpath:phase_create')
    def get(self, request, ebook_pk) :
        ebook = get_object_or_404(Ebook, id=ebook_pk, creator=request.user)
        creators = UserProfile.objects.all().filter(creator=True).exclude(user=request.user)
        
        try:
            payment_splits = EbookPaymentSplits.objects.filter(ebook=ebook)
            creator_share = 100
            for payment_split in payment_splits:
                creator_share -= payment_split.amount


            form = EbookPaymentSplitsForm(instance=payment_splits)
        except:
            form = EbookPaymentSplitsForm()
        ctx = { 'form' : form, 'ebook':ebook, 'payment_splits': payment_splits, 'creators': creators, 'creator_share':creator_share}
        return render(request, self.template_name, ctx)

    def post(self, request, ebook_pk) :
        # form = CourseAddResourcesForm(self.request.POST)

        # if not form.is_valid():
        #     ctx = {'form' : form}
        #     return render(request, self.template_name, ctx)

        # Add creator to the model before saving
        # course_form = form.save(commit=False)
        # course = Course.objects.get(id=course_pk)
        # course_form.course = course
        # course_form.save()
        e = Ebook.objects.get(id=ebook_pk)
        if request.user == e.creator:

            payload = request.POST.dict()
            
            users = []
            payout = []
            for key, value in payload.items():
                if 'csrf' not in key and 'owner' not in key:
                    # if int(key[-1]): 
                    payout.append(value)
                    if 'amount' in key:
                        users.append(payout)
                        payout = []


            print("top-level payment splits: ", users)

            # drop resources associated with course id and creator id
            EbookPaymentSplits.objects.all().filter(ebook=e).delete()

            #insert new course data
            total_percentage_amount = 0

            for split in users:
                amount = int(split[1])
                total_percentage_amount += amount
                if total_percentage_amount >= 100:
                    messages.error(request, "Please ensure that all of the amounts total to less than or equal to 100.")
                    creators = UserProfile.objects.all().filter(creator=True).exclude(user=request.user)
                    try:
                        ebook_payment_splits = EbookPaymentSplits.objects.filter(ebook=e)
                        form = EbookPaymentSplitsForm(instance=ebook_payment_splits)
                    except:
                        form = EbookPaymentSplitsForm()
                    ctx = { 'form' : form, 'ebook':e, 'payment_splits': ebook_payment_splits, 'creators': creators}
                    return render(request, self.template_name, ctx)

            for split in users:
                print(split)
                creator = User.objects.get(id=int(split[0]))
                amt = int(split[1])
                print("ebook", e, "creator", creator, "amount", amt)
                ebook_splits = EbookPaymentSplits.objects.create(ebook=e, user=creator, amount=amt).save()


            return redirect(reverse('criticalpath:ebook_detail', args=[ebook_pk]))
        else:
            return redirect(reverse(['home']))

class EbookDetailView(OwnerDetailView):
    model = Ebook
    template_name =  "criticalpath/ebook_detail.html"
    def get(self, request, ebook_pk) :
        # p = Phase.objects.get(id=phase_pk)
        if request.user.is_authenticated:
            e = get_object_or_404(Ebook, id=ebook_pk)
            p = Purchase.objects.all().filter(ebook=e, user=request.user)
            if e.creator == request.user or p or e.price == 0:
                context = { 'ebook' : e }
                return render(request, self.template_name, context)

            else:
                messages.error(request, "You must first purchase this ebook.")
                return redirect(reverse('marketplace:ebook_purchase_detail', args=[r.id]))
        else:
            e = get_object_or_404(Ebook, id=ebook_pk)
            if e.price == 0:
                    context = { 'ebook' : e}
                    return render(request, self.template_name, context)
            else:
                messages.error(request, "You must first login.")
                return redirect(reverse('signin'))

class EbookUpdateView(OwnerUpdateView):
    template_name =  "criticalpath/ebook_form.html"
    def get(self, request, ebook_pk) :
        ebook = get_object_or_404(Ebook, id=ebook_pk, creator=self.request.user)

        form = EbookForm(instance=ebook)
        ctx = { 'form': form, "header_name": "Update Ebook", "ebook" : ebook }
        return render(request, self.template_name, ctx)

    def post(self, request, ebook_pk) :
        ebook = get_object_or_404(Ebook, id=ebook_pk, creator=self.request.user)

        form = EbookForm(request.POST, request.FILES or None, instance=ebook)


        if not form.is_valid() :
            ctx = {'form' : form}
            return render(request, self.template_name, ctx)

        ebook = form.save(commit=False)

        print(ebook)
        print(ebook.price, ebook.currency_type.iso_code)
        if ebook.price >= 250000 and ebook.currency_type.iso_code == "SAT":
            messages.error(request, "Price cannot be greater than 250,000 sats")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)        
        elif ebook.price > 25 and ebook.currency_type.iso_code == "USD":
            messages.error(request, "Price cannot be greater than $25.")

            ctx = {'form' : form}
            return render(request, self.template_name, ctx)       
        ebook.save()

        return redirect(reverse('criticalpath:ebook_add_splits', args=[ebook.id]))

class EbookDeleteView(OwnerDeleteView):
    model = Ebook
    template_name = "criticalpath/ebook_confirm_delete.html"
    def get(self, request, ebook_pk) :
        ebook = get_object_or_404(Ebook, id=ebook_pk, creator=self.request.user)
        ctx = { 'ebook' : ebook }
        return render(request, self.template_name, ctx)
    def post(self, request, ebook_pk):
        ebook = get_object_or_404(Ebook, id=ebook_pk, creator=self.request.user)
        # consider moving to an archive status instead of deleting.
        # exclude archive view from creator but still allow it to be viewed as a part of courses
        # allow existing purchased users to still view the content
        # disclude discovery from marketplace though by excluding any archived courses
        ebook.delete()
        return redirect(reverse('criticalpath:my-creations'))



# class ObjectiveListView(View):
#     model = Objective
#     fields = ['text']


#     def get(self, request) :
#         objective_list = Objective.objects.all()
#         favorites = list()
#         if request.user.is_authenticated:
#             # rows = [{'id': 2}, {'id': 4} ... ]  (A list of rows)
#             rows = request.user.favorite_objectives.values('id')
#             # favorites = [2, 4, ...] using list comprehension
#             favorites = [ row['id'] for row in rows ]
#         strval =  request.GET.get("search", False)
#         if strval :
#             # Simple title-only search
#             # objects = Post.objects.filter(title__contains=strval).select_related().order_by('-updated_at')[:10]

#             # Multi-field search
#             query = Q(title__contains=strval)
#             query.add(Q(description__contains=strval), Q.OR)
#             objects = Objective.objects.filter(query).select_related().order_by('-updated_at')[:10]
#         else :
#             # try both versions with > 4 posts and watch the queries that happen
#             objects = Objective.objects.all().order_by('-updated_at')[:10]
#             # objects = Post.objects.select_related().all().order_by('-updated_at')[:10]

#         # Augment the post_list
#         for obj in objects:
#             obj.natural_updated = naturaltime(obj.updated_at)

#         ctx = {'objective_list' : objects, 'search' : strval, 'favorites' : favorites }
#         retval = render(request, self.template_name, ctx)

#         dump_queries()
#         return retval;



class CommentCreateView(LoginRequiredMixin, View):
    def post(self, request, pk) :
        d = get_object_or_404(Journey, id=pk)
        comment = Comment(text=request.POST['comment'], creator=request.user, journey=d)
        comment.save()
        return redirect(reverse('criticalpath:journey_detail', args=[d.id]))

class CommentDeleteView(OwnerDeleteView):
    model = Comment
    template_name =  "criticalpath/comment_delete.html"

    # https://stackoverflow.com/questions/26290415/deleteview-with-a-dynamic-success-url-dependent-on-id
    def get_success_url(self):
        journey = self.object.journey
        return reverse('criticalpath:journey_detail', args=[journey.id])

# csrf exemption in class based views
# https://stackoverflow.com/questions/16458166/how-to-disable-djangos-csrf-validation
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.utils import IntegrityError

# @method_decorator(csrf_exempt, name='dispatch')
# class AddFavoriteView(LoginRequiredMixin, View):
#     def post(self, request, pk) :
#         print("Add PK",pk)
#         d = get_object_or_404(Journey, id=pk)
#         fav = Fav(user=request.user, journey=d)
#         try:
#             fav.save()  # In case of duplicate key
#         except IntegrityError as e:
#             pass
#         return HttpResponse()

# @method_decorator(csrf_exempt, name='dispatch')
# class DeleteFavoriteView(LoginRequiredMixin, View):
#     def post(self, request, pk) :
#         print("Delete PK",pk)
#         d = get_object_or_404(Journey, id=pk)
#         try:
#             fav = Fav.objects.get(user=request.user, journey=d).delete()
#         except Fav.DoesNotExist as e:
#             pass

#         return HttpResponse()

@login_required
def reward_user(request, course_pk, resource_pk):
    resource = get_object_or_404(Resource, id=resource_pk)
    print(resource)
    
    # this is only really concerning if we have a purchase amount on a resource that is less than 100 sats. because we are paying out 10 sats. if they sell a resource for less than 10 and earn 10, then there's a problem.
    # we will need to update this USD later on.
    if resource.price <= 10:
        if resource.price != 0:
            purchase = get_object_or_404(Purchase, resource=resource, user=request.user)
        # check if the resource is in a featured course
        # if the resource isn't in a course, then it's not a featured resource
        courses_resource_is_included_in = CourseResources.objects.all().filter(resource=resource)
        foundFeaturedCourse = False

        if courses_resource_is_included_in.count()  > 0:
            for course in courses_resource_is_included_in:
                # if the course isn't in the featured list, it can be botted.
                get_course = Course.objects.all().filter(id=course.course.id)
                courses = FeaturedCourses.objects.all().filter(course__in=get_course)

                if courses.count() > 0:
                    foundFeaturedCourse = True
        
        if not foundFeaturedCourse:
            messages.success(request, ("Only resources a part of the featured marketplace are able to be earned on."))
            return redirect(reverse('criticalpath:course_resource_detail', args=[course_pk, resource.id]))


    # make sure only paid resources are rewarded to ensure no bot issues.
    # I am removing paid resource requirements for now. 
    # if int(resource.price) == 0:
    #     messages.success(request, ("This resource is not eligible for a reward. Only paid resources are eligible."))
    #     return redirect(reverse('criticalpath:resource_detail', args=[resource.id]))
    
    if resource.creator == request.user:
        messages.success(request, ("You cannot earn a reward on your own resource."))
        return redirect(reverse('criticalpath:course_resource_detail', args=[course_pk, resource.id]))

    # check if the user has already been rewarded
    reward = Reward.objects.all().filter(resource=resource, user=request.user)
    if reward:
        messages.success(request, ("You have already been rewarded for completing this resource."))
        return redirect(reverse('criticalpath:course_resource_detail', args=[course_pk, resource.id]))
    # user is eligible for reward
    # payout amount will be 1 for now
    payout_amount = 1
    # get transaction code
    t_code = TransactionCode.objects.get(transaction_code_text="Resource Reward")
    
    
    # create reward transaction
    transaction = Transaction.objects.create(
                        description=f"{request.user} completed {resource.title} for a reward of {payout_amount}",
                        user=request.user,
                        amount=payout_amount,
                        transaction_code=t_code
                        )

    # create reward for analytics
    reward = Reward.objects.create(
                        user=request.user,
                        resource=resource,
                        transaction=transaction
                        ).save()

    # credit the learner with their 1 sat reward
    learner_wallet = Wallet.objects.get(user=request.user)
    new_balance = learner_wallet.balance + payout_amount
    update_balance_data = {
        "balance": new_balance,
    }
    Wallet.objects.filter(user=request.user).update(**update_balance_data)

    messages.success(request, ("Congrats on completing this resource! You are awesome. You have been rewarded with 1 sat."))
    return redirect(reverse('criticalpath:course_resource_detail', args=[course_pk, resource.id]))

def creator_signup(request):
    if request.POST:
        print(request.POST)
        if request.POST["agree"]:
            creator_flag = {
                "creator": True,
            }
            UserProfile.objects.filter(user=request.user).update(**creator_flag)
            messages.success(request, ("Nice! You've signed-up for creator."))
            return redirect(reverse('criticalpath:my-creations'))
        else:
            messages.error(request, ("Please accept the terms to continue."))
            return redirect(reverse('criticalpath:my-creations'))