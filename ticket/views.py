import json
from datetime import datetime, timedelta

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model # as per https://docs.djangoproject.com/en/dev/topics/auth/customizing/#referencing-the-user-model
from django.contrib import messages
from django.db.models import Count
from django.db.models import Q
import django.forms
from django.forms.utils import ErrorList
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, UpdateView, FormView

from django.db.models import Count, Sum

from core.mixins import JSONResponseMixin, CSVorJSONResponseMixin, PrettyPaginatorMixin
from core.utils import *
from id.models import Network
from ticket.utils import *
from ticket.mixins import *
from ticket.models import Ticket, PersonTicket, CompanyTicket, OtherTicket, TicketUpdate, TicketCharge, Budget
from ticket import forms
from ticket import constants

from podaci import PodaciMixin
from podaci.models import PodaciTag, PodaciFile

class CompanyTicketUpdate(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = CompanyTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.CompanyTicketForm

    def get_context_data(self, **kwargs):
        context = super(CompanyTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['company_ownership_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(CompanyTicketUpdate, self).__init__(*args, **kwargs)

class OtherTicketUpdate(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = OtherTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.OtherTicketForm

    def get_context_data(self, **kwargs):
        context = super(OtherTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['other_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(OtherTicketUpdate, self).__init__(*args, **kwargs)

class PersonTicketUpdate(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = PersonTicket
    template_name = 'tickets/request.jinja'
    form_class = forms.PersonTicketForm

    def get_context_data(self, **kwargs):
        context = super(PersonTicketUpdate, self).get_context_data(**kwargs)
        context['ticket'] = self.get_object()
        context['person_ownership_form'] = context['form']
        return context

    def __init__(self, *args, **kwargs):
        super(PersonTicketUpdate, self).__init__(*args, **kwargs)


class TicketActionBaseHandler(TicketUpdateMixin, UpdateView):
    model = Ticket
    form_class = forms.TicketCancelForm

    success_messages = None
    failure_messages = None
    force_invalid = False

    def perform_invalid_action(self, form):
        return

    def perform_valid_action(self, form):
        return

    def form_invalid(self, form):
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.object.id}))
        #return super(TicketActionBaseHandler, self).form_invalid(form)

    def form_valid(self, form):
        self.perform_valid_action(form)

        if self.force_invalid is True:
            return self.form_invalid(form)

        return super(TicketActionBaseHandler, self).form_valid(form, self.success_messages)

    def get_success_url(self):
        ticket = self.get_object()
        return reverse_lazy('ticket_details', kwargs={'ticket_id': ticket.id})

class TicketActionCancel(TicketActionBaseHandler):

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to cancel the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object
        ticket.status = constants.get_choice('Cancelled', constants.TICKET_STATUS)
        self.perform_ticket_update(ticket, 'Cancelled', form.cleaned_data['reason'])
        return super(TicketActionCancel, self).perform_valid_action(form)

class TicketActionClose(TicketActionBaseHandler):

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to close the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object
        ticket.status = constants.get_choice('Closed', constants.TICKET_STATUS)
        self.perform_ticket_update(ticket, 'Closed', form.cleaned_data['reason'])
        return super(TicketActionClose, self).perform_valid_action(form)


class TicketActionJoin(TicketActionBaseHandler, PodaciMixin):
    form_class = forms.TicketEmptyForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error adding you to the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        tag = ticket.get_tag()

        if self.request.user.is_staff or self.request.user.is_superuser:
            ticket.responders.add(self.request.user)
            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', self.request.user.display_name + unicode(_(' has joined the ticket')))
            self.transition_ticket_from_new(ticket)
            tag.add_user(self.request.user, True)
            return super(TicketActionJoin, self).perform_valid_action(form)

        elif self.request.user.is_volunteer:
            ticket.volunteers.add(self.request.user)
            self.success_messages = [_('You have successfully been added to the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Joined', self.request.user.display_name + unicode(_(' has joined the ticket')))
            self.transition_ticket_from_new(ticket)
            tag.add_user(self.request.user, True)
            return super(TicketActionJoin, self).perform_valid_action(form)

        else:
            self.perform_invalid_action(form)

class TicketActionLeave(TicketActionBaseHandler, PodaciMixin):
    form_class = forms.TicketEmptyForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error removing you from the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        tag = ticket.get_tag()

        if self.request.user in ticket.responders.all():
            ticket.responders.remove(self.request.user)
            tag.remove_user(self.request.user)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.user.display_name + unicode(_(' has left the ticket')))

            return super(TicketActionLeave, self).perform_valid_action(form)
        elif self.request.user in ticket.volunteers.all():
            ticket.volunteers.remove(self.request.user)
            tag.remove_user(self.request.user)
            self.success_messages = [_('You have successfully been removed from the ticket.')]
            self.perform_ticket_update(ticket, 'Responder Left', self.request.user.display_name + unicode(_(' has left the ticket')))

            return super(TicketActionLeave, self).perform_valid_action(form)
        else:
            self.force_invalid = True


class TicketActionOpen(TicketActionBaseHandler):

    def perform_invalid_action(self, form):
        messages.error(self.request, _('A reason must be supplied to (re)open the ticket.'))

    def perform_valid_action(self, form):
        ticket = self.object

        if(ticket.volunteers.count() == 0 and ticket.responders.count() == 0):
            ticket.status = constants.get_choice('New', constants.TICKET_STATUS)
        else:
            ticket.status = constants.get_choice('In Progress', constants.TICKET_STATUS)

        self.perform_ticket_update(ticket, 'Opened', form.cleaned_data['reason'])

        return super(TicketActionOpen, self).perform_valid_action(form)


class TicketAddCharge(TicketActionBaseHandler):
    form_class = forms.RequestChargeForm

    def perform_invalid_action(self, form):
        messages.error(self.request, _('Error adding charge.'))

    def perform_valid_action(self, form):
        charge = TicketCharge(
            ticket=self.object,
            user=self.request.user,
            item=form.cleaned_data['item'],
            cost=form.cleaned_data['cost'],
            cost_original_currency=form.cleaned_data['cost_original_currency'],
            original_currency=form.cleaned_data['original_currency']
        ).save()

        self.perform_ticket_update(self.object,
                                   'Charge Added',
                                   "$%.2f" % float(form.cleaned_data['cost']) + " - " + form.cleaned_data['item'])
        return super(TicketAddCharge, self).perform_valid_action(form)


class TicketAdminSettingsHandler(TicketUpdateMixin, UpdateView, PodaciMixin):
    model = Ticket
    template_name = "modals/form_basic.jinja"
    form_class = forms.TicketAdminSettingsForm
    redirect = "ticket_list"
    """
    Administrator edits a ticket's properties (re-assignment, closing, etc)
    """

    def convert_users_to_ids(self, users):
        return [int(i.id) for i in users]

    def form_invalid(self, form):
        messages.error(self.request, _('There was an error updating the ticket.'))
        return HttpResponseRedirect(reverse(self.redirect))

    def form_valid(self, form):
        ticket = self.object
        form_responders = [int(i) for i in form.cleaned_data['responders']]
        form_volunteers = [int(i) for i in form.cleaned_data['volunteers']]

        current_responders = self.convert_users_to_ids(ticket.responders.all())
        current_volunteers = self.convert_users_to_ids(ticket.volunteers.all())

        tag = ticket.get_tag()

        if 'redirect' in self.request.POST:
            self.redirect = self.request.POST['redirect']

        if len(form_responders) > 0 or len(form_volunteers) > 0:
            self.transition_ticket_from_new(ticket)

        for i in form_responders:
            if i not in current_responders:
                u = get_user_model().objects.get(pk=i)
                tag.add_user(u, True)
                self.perform_ticket_update(ticket, 'Responder Joined', u.display_name + unicode(_(' has joined the ticket')))

        for i in form_volunteers:
            if i not in current_volunteers:
                u = get_user_model().objects.get(pk=i)
                tag.add_user(u, True)
                self.perform_ticket_update(ticket, 'Responder Joined', u.display_name + unicode(_(' has joined the ticket')))

        for i in current_responders:
            if i not in form_responders:
                u = get_user_model().objects.get(pk=i)
                tag.remove_user(u)
                self.perform_ticket_update(ticket, 'Responder Left', u.display_name + unicode(_(' has left the ticket')))

        for i in current_volunteers:
            if i not in form_volunteers:
                u = get_user_model().objects.get(pk=i)
                tag.remove_user(u)
                self.perform_ticket_update(ticket, 'Responder Left', u.display_name + unicode(_(' has left the ticket')))

        return super(TicketAdminSettingsHandler, self).form_valid(form)

    def get(self, request, pk, redirect, status='success'):
        super(TicketAdminSettingsHandler, self).get(self, request)
        self.redirect = redirect

        t = render_to_string('modals/form_basic.jinja', self.get_context_data())
        return JsonResponse({'status': status, 'html': t})

    def get_context_data(self, **kwargs):
        context = super(TicketAdminSettingsHandler, self).get_context_data(**kwargs)
        context['csrf'] = get_token(self.request)
        context['form_action'] = reverse_lazy('ticket_admin_settings', kwargs={'pk': self.object.id, 'redirect': self.redirect})
        context['form'] = self.get_form(self.form_class)
        context['form'].fields['redirect'].initial = self.redirect
        return context

    def get_success_url(self):
        try:
            response = reverse_lazy(self.redirect)
            return respose
        except Exception:
            pass

        response = reverse_lazy(self.redirect, kwargs={'ticket_id': self.object.id})
        return response


class TicketUpdateRemoveHandler(TicketActionBaseHandler):
    # it should be noted that while the intent of this handler
    # is to eventually cater to removing any ticket updates that
    # would be neccesary to remove, right now the assumption is
    # just for comments - 2014.03.22
    model = TicketUpdate
    form_class = forms.TicketEmptyForm
    ticket = None

    def get_ticket(self):
        self.ticket = Ticket.objects.get(pk=self.object.ticket_id)

    def form_invalid(self, form):
        self.get_ticket()
        self.perform_invalid_action(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.ticket.id}))

    def form_valid(self, form):
        self.get_ticket()
        self.perform_valid_action(form)
        super(TicketUpdateRemoveHandler, self).form_valid(form)
        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": self.ticket.id}))

    def perform_invalid_action(self, form):
        messages.error(self.request, _('There was an error deleting the comment.'))

    def perform_valid_action(self, form):
        self.success_messages = [_('The comment was successfully deleted.')]
        self.object.is_removed = True
        self.object.save()
        return super(TicketUpdateRemoveHandler, self).perform_valid_action(form)

    def __init__(self, *args, **kwargs):
        super(TicketUpdateRemoveHandler, self).__init__(*args, **kwargs)


class TicketDetail(TemplateView, PodaciMixin):
    template_name = "tickets/request_details.jinja"
    """
    View for the requester of a ticket to view what is currently going on,
    and provide feedback / close the request / etc
    """
    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def dispatch(self, request, ticket_id=None):
        self.ticket = Ticket.objects.get(id=int(ticket_id))
        if hasattr(self.ticket, "personticket"):
            self.ticket = self.ticket.personticket
        elif hasattr(self.ticket, "companyticket"):
            self.ticket = self.ticket.companyticket
        elif hasattr(self.ticket, "otherticket"):
            self.ticket = self.ticket.otherticket
        else:
            print dir(self.ticket)
            raise ValueError("Unknown ticket type")

        if not self.ticket:
            return self.abort(404)

        # if not self.ticket.is_public and not (
        #     request.user.is_superuser or
        #     request.user == self.ticket.requester or
        #     request.user in self.ticket.responders.all() or
        #     request.user in self.ticket.volunteers.all()):
        #         return self.abort(401)

        self.form = forms.CommentForm()
        #form.author.data = request.user.id
        # form.ticket.data = ticket.id
        return super(TicketDetail, self).dispatch(request)

    def get_context_data(self):
        ticket_updates = (TicketUpdate.objects
                          .filter(ticket=self.ticket, is_removed=False)
                          .order_by("-created"))

        charges = (TicketCharge.objects.filter(ticket=self.ticket)
                   .order_by("created"))

        outstanding = sum([x.cost for x in TicketCharge.objects.filter(reconciled=False)])

        tag = self.ticket.get_tag()

        can_join_leave = False
        if self.request.user != self.ticket.requester:
            if self.request.user.is_volunteer and self.ticket.is_public:
                can_join_leave = True

            if self.request.user.is_volunteer and self.request.user in self.ticket.volunteers.all():
                can_join_leave = True

            if self.request.user.is_superuser or self.request.user.is_staff:
                can_join_leave = True

        return {
            'ticket': self.ticket,
            'ticket_updates': ticket_updates,
            'charges': charges,
            'charges_outstanding': outstanding,
            'ticket_update_form': self.form,
            'cancel_form': forms.TicketCancelForm(),
            'mark_paid_form': forms.TicketPaidForm(),
            'close_form': forms.TicketCancelForm(),
            'open_form': forms.TicketCancelForm(),
            'flag_form': forms.RequestFlagForm(),
            'tag': tag,
            'result_files': tag.list_files(),
            'charge_form': forms.RequestChargeForm(),
            'ticket_detail_view': True,
            'can_join_leave': can_join_leave
        }

    #FIXME: AJAXize!
    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, request):
        form = forms.CommentForm(self.request.POST)

        if not form.is_valid():
            return self.get(request)

        comment = form.save(commit=False)
        comment.ticket = self.ticket
        comment.author = request.user
        comment.save()
        return HttpResponseRedirect(reverse('ticket_details', kwargs={ "ticket_id":self.ticket.id}))

class TicketList(PrettyPaginatorMixin, CSVorJSONResponseMixin, TemplateView, PodaciMixin):
    template_name = "tickets/request_list.jinja"
    page_name = ""
    ticket_list_name = ""
    tickets = []
    page_number = 1
    page_size = 10
    page_buttons = 5
    page_buttons_padding = 2
    paginator = None
    url_name = 'ticket_list'
    url_args = {}
    CONTEXT_ITEMS_KEY = "tickets"
    CONTEXT_TITLE_KEY = "page_name"

    def get_context_data(self, **kwargs):
        self.filter_terms = self.request.GET.get("filter", '')

        if 'page' in kwargs:
            self.page_number = int(kwargs.pop('page'))
            if self.page_number is None:
                self.page_number = 1

        context = {
            'page_name': self.page_name,
            'ticket_list_name': self.ticket_list_name,
            'tickets': self.get_paged_tickets(self.page_number),
            'paginator_object': self.create_pretty_pagination_object(self.paginator,
                                                                     self.page_number,
                                                                     self.page_buttons,
                                                                     self.page_buttons_padding,
                                                                     self.url_name,
                                                                     self.url_args),
            'page_number': self.page_number,
            'ticket_figures': self.get_ticket_list_figures(),
            'filter_terms': self.filter_terms
        }

        return context

    def get_ticket_list_figures(self):
        ticket_figures = {
            'all_open': TicketListAllOpen().get_ticket_set(self.request.user).count(),
            'all_closed': TicketListAllClosed().get_ticket_set(self.request.user).count(),
            'my_open': TicketListMyOpen().get_ticket_set(self.request.user).count(),
            'my_closed': TicketListMyClosed().get_ticket_set(self.request.user).count(),
            'my_assigned': TicketListMyAssigned().get_ticket_set(self.request.user).count(),
            'my_assigned_closed': TicketListMyAssignedClosed().get_ticket_set(self.request.user).count(),
            'public': TicketListPublic().get_ticket_set(self.request.user).count(),
            'public_closed': TicketListPublicClosed().get_ticket_set(self.request.user).count(),
            'unassigned': TicketListUnassigned().get_ticket_set(self.request.user).count(),
            'upcoming_deadline': TicketListUpcomingDeadline().get_ticket_set(self.request.user).count()
        }

        return ticket_figures

    def get_paged_tickets(self, page_number):
        self.set_paginator_object()

        try:
            paged_tickets = self.paginator.page(page_number)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            paged_tickets = self.paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            paged_tickets = self.paginator.page(self.paginator.num_pages)

        return paged_tickets

    def set_paginator_object(self):
        ticket_set = self.get_ticket_set(self.request.user)
        if self.filter_terms:
            ticket_set = ticket_set.filter(Q(requester__email__contains=self.filter_terms)
                                         | Q(requester__first_name__contains=self.filter_terms)
                                         | Q(requester__last_name__contains=self.filter_terms))
        self.paginator = Paginator(get_actual_tickets(ticket_set), self.page_size)

    def get_ticket_set(self, user):
        return self.tickets

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(TicketList, self).dispatch(*args, **kwargs)


class TicketListAllOpen(TicketList):
    page_name = "All Requests"
    ticket_list_name = "All Open Requests"
    url_name = 'ticket_all_open_list'

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")

class TicketListAllClosed(TicketList):
    page_name = "All Requests"
    ticket_list_name = "All Closed Requests"
    url_name = 'ticket_all_closed_list'

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")

class TicketListMyOpen(TicketList):
    page_name = "My Requests"
    ticket_list_name = "My Open Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            requester=user).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")

class TicketListMyClosed(TicketList):
    page_name = "My Requests"
    ticket_list_name = "My Closed Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            requester=user).filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")

class TicketListMyAssigned(TicketList):
    page_name = "My Assignments"
    ticket_list_name = "Open Assignments"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            Q(responders__in=[user]) | Q(volunteers__in=[user])).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")

class TicketListMyAssignedClosed(TicketList):
    page_name = "My Assignments"
    ticket_list_name = "Closed Assignments"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            Q(responders__in=[user]) | Q(volunteers__in=[user])).filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")


class TicketListPublic(TicketList):
    page_name = "Public Requests"
    ticket_list_name = "Open Public Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            is_public=True).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")

class TicketListPublicClosed(TicketList):
    page_name = "Pubic Requests"
    ticket_list_name = "Closed Public Requests"

    def get_ticket_set(self, user):
        return Ticket.objects.filter(
            is_public=True).filter(
            Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")


class TicketListUnassigned(TicketList):
    page_name = "Unassigned Requests"
    ticket_list_name = "Unassigned Requests"
    url_name = 'ticket_unassigned_list'

    def get_ticket_set(self, user):
        return Ticket.objects.annotate(
            volunteer_count=Count('volunteers')).annotate(
            responder_count=Count('responders')).filter(
            Q(volunteer_count=0) & Q(responder_count=0)).order_by(
            "-created")


class TicketListUpcomingDeadline(TicketList):
    page_name = "Upcoming Deadline Requests"
    ticket_list_name = "Requests with deadlines in the 30 days"
    url_name = 'ticket_deadline_list'

    def get_ticket_set(self, user):
        filter_date = datetime.now() + timedelta(days=30)

        return Ticket.objects.filter(
            Q(deadline__isnull=False) & Q(deadline__lte=filter_date)).filter(
            ~Q(status=constants.get_choice('Closed', constants.TICKET_STATUS))).order_by(
            "-created")


class TicketRequest(TemplateView, PodaciMixin):
    template_name = "tickets/request.jinja"

    # runs when django forms clean the data but before django saves the object

    """ Some registered user submits a ticket for response by a responder. """
    def dispatch(self, *args, **kwargs):

        if self.request.method == 'POST':
            self.ticket_type_form = forms.TicketTypeForm(self.request.POST,
                                                         prefix='ticket_type')

            self.forms = {
                'ticket_type_form': self.ticket_type_form,
                'person_ownership_form': forms.PersonTicketForm(
                    self.request.POST,
                    prefix='person'),
                'company_ownership_form': forms.CompanyTicketForm(
                    self.request.POST,
                    prefix='company'),
                'other_form': forms.OtherTicketForm(
                    self.request.POST,
                    prefix='other')
            }
        else:
            self.forms = {
                'ticket_type_form': forms.TicketTypeForm(prefix='ticket_type'),
                'person_ownership_form': forms.PersonTicketForm(prefix='person'),
                'company_ownership_form': forms.CompanyTicketForm(prefix='company'),
                'other_form': forms.OtherTicketForm(prefix='other'),
            }
        return super(TicketRequest, self).dispatch(self.request)

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer',
    #         fail_redirect=('request_unauthorized',))  # Reversed by role_in
    def get_context_data(self, ticket_id=None):
        ctx = {
            'ticket': None
        }
        ctx.update(self.forms)
        return ctx

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, ticket_id=None):
        if not self.forms["ticket_type_form"].is_valid():
            print self.forms["ticket_type_form"].errors.as_data()
            # self.add_message("Error")
            return

        ticket_type = self.forms["ticket_type_form"].cleaned_data["ticket_type"]
        form = self.forms[ticket_type+"_form"]

        # print "ticket info"
        # print " "
        # print " "
        # print ticket_type
        # print form.errors.as_data()
        # print "end form"

        if not form.is_valid():
            # self.add_message(_("Error: Form was not valid"))
            print "FORM ERROR NOT VALID!!!"
            return self.get(None)

        ticket = form.save(commit=False)
        ticket.requester = self.request.user
        ticket.save()
        messages.success(self.request, _('Ticket successfully created.'))

        tag = ticket.get_tag()

        return HttpResponseRedirect(reverse('ticket_details', kwargs={"ticket_id": ticket.id}))


class TicketUserFeesOverview(CSVorJSONResponseMixin, TemplateView):
    template_name = 'tickets/ticket_user_fees_overview.jinja'
    CONTEXT_ITEMS_KEY = "users"

    def get_context_data(self):
        return {
            "title": "User Fees",
            "users": get_user_model().objects.annotate(payment_count=Count('ticketcharge')).annotate(payment_total=Sum('ticketcharge__cost')).filter(payment_count__gt=0)
        }

class TicketNetworkFeesOverview(CSVorJSONResponseMixin, TemplateView):
    template_name = 'tickets/ticket_network_fees_overview.jinja'
    CONTEXT_ITEMS_KEY = "networks"

    def get_context_data(self):
        return {
            "title": "Network Fees",
            "networks": Network.objects.all(),
        }

class TicketBudgetFeesOverview(CSVorJSONResponseMixin, TemplateView):
    template_name = 'tickets/ticket_budget_fees_overview.jinja'
    CONTEXT_ITEMS_KEY = "budgets"

    def get_context_data(self):
        return {
            "title": "Budget Fees",
            "budgets": Budget.objects.all(),
        }

class TicketResolutionWorkload(TemplateView):
    template_name = 'tickets/ticket_resolution_workload.jinja'

    def get_context_data(self):
        researchers = get_user_model().objects.filter(
            Q(is_volunteer=True) | Q(is_staff=True) | Q(is_superuser=True)
        )
        sort = self.request.GET.get("sort", "role")
        if sort == "role":
            researchers = researchers.order_by("-is_superuser", "-is_staff",
                "-is_volunteer")
        #elif sort == "time":
        #    researchers = researchers.annotate(open_tickets=Count('ticket__'))

        return {
            "researchers": researchers
        }

class TicketResolutionTime(TemplateView):
    template_name = 'tickets/ticket_resolution_time.jinja'

    def get_context_data(self):
        tickets = Ticket.objects.filter(status="closed")[:100]
        times = [x.resolution_time() for x in tickets]
        if len(times) == 0:
            average_timedelta = timedelta(0)
        else:
            average_timedelta = sum(times, timedelta(0)) / len(times)

        return {
            "averagetime": average_timedelta,
            "count": tickets.count()
        }

class TicketReport(CSVorJSONResponseMixin, TemplateView):
    template_name = 'tickets/ticket_report.jinja'
    CONTEXT_ITEMS_KEY = "tickets"

    def get_context_data(self):
        startdate = self.request.GET.get('startdate', None)
        enddate = self.request.GET.get('enddate', None)

        tickets = Ticket.objects.all()
        if startdate:
            tickets = tickets.filter(created__gt=startdate)
        if enddate:
            tickets = tickets.filter(created__lte=enddate)

        return {'tickets': tickets, 'title': 'Ticket report'}
