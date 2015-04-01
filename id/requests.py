from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views.generic import (
        TemplateView, ListView, RedirectView, UpdateView,
        CreateView, FormView, View)
from django.utils.translation import ugettext_lazy as _
from id.mixins import JSONResponseMixin, MessageMixin
from id import models
from ticket import forms
from ticket.models import (
    Ticket, TicketUpdate, TicketCharge,
    PersonTicket, CompanyTicket, OtherTicket
)

# FIXME: Authentication

class RequestUnauthorized(TemplateView, MessageMixin):
    def _get(self):
        if models.AccountRequest.pending_for(self.user):
            self.add_message(_("Your request for an account is pending."
                        " Once approved, you can access Ask an Expert"))
            view_name = 'home'
        else:
            self.add_message(_("In order to access Ask an Expert,"
                       " please request an account type."))
            view_name = 'request_account_home'
        return self.redirect(self.uri_for(view_name))


class RequestHandler(TemplateView, MessageMixin):
    template_name = "tickets/request.jinja"

    """ Some registered user submits a ticket for response by a responder. """
    def dispatch(self, request):
        self.ticket = None
        if request.method == 'POST':
            self.ticket_type_form = forms.TicketTypeForm(self.request.POST,
                                                         prefix='ticket_type')

            if 'ticket_id' in self.kwargs:
                ticket_id = int(self.kwargs['ticket_id'])
                self.ticket = models.Ticket.objects.get_by_id(ticket_id)
                self.ticket_type_form.ticket_type.data = self.ticket.ticket_type

            self.forms = {
                'ticket_type_form': self.ticket_type_form,
                'person_ownership_form': forms.PersonTicketForm(
                    self.request.POST, 
                    prefix='person', 
                    instance=self.ticket),
                'company_ownership_form': forms.CompanyTicketForm(
                    self.request.POST, 
                    prefix='company', 
                    instance=self.ticket),
                'other_form': forms.OtherTicketForm(
                    self.request.POST, 
                    prefix='other', 
                    instance=self.ticket)
            }
        else:
            self.forms = {
                'ticket_type_form': forms.TicketTypeForm(prefix='ticket_type'),
                'person_ownership_form': forms.PersonTicketForm(prefix='person'),
                'company_ownership_form': forms.CompanyTicketForm(prefix='company'),
                'other_form': forms.OtherTicketForm(prefix='other'),
            }
        return super(RequestHandler, self).dispatch(request)

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer',
    #         fail_redirect=('request_unauthorized',))  # Reversed by role_in
    def get_context_data(self, ticket_id=None):
        ctx = {
            'ticket': self.ticket
        }
        ctx.update(self.forms)
        return ctx

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, ticket_id=None):
        if not self.forms["ticket_type_form"].is_valid():
            self.add_message("Error")
            return

        ticket_type = self.forms["ticket_type_form"].cleaned_data["ticket_type"]
        form = self.forms[ticket_type+"_form"]

        if not form.is_valid():
            self.add_message(_("Error: Form was not valid"))
            print "FORM ERROR NOT VALID!!!"
            return self.get(None)

        ticket = form.save(commit=False)
        ticket.requester = self.request.user
        ticket.save()

        if ticket_id:
            self.add_message(_('Ticket successfully saved.'))
        else:
            self.add_message(_('Ticket successfully created.'))

        return HttpResponseRedirect(reverse('request_details', kwargs={"ticket_id": ticket.id}))


class RequestDetailsHandler(TemplateView):
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

        if not self.ticket.is_public and not (
            request.user.is_superuser or
            request.user == self.ticket.requester or
            request.user in self.ticket.responders.objects.all() or
            request.user in self.ticket.volunteers.objects.all()):
            return self.abort(401)

        self.form = forms.CommentForm()
        #form.author.data = request.user.id
        # form.ticket.data = ticket.id
        return super(RequestDetailsHandler, self).dispatch(request)

    def get_context_data(self):
        ticket_updates = (TicketUpdate.objects
                          .filter(ticket=self.ticket)
                          .order_by("created"))

        charges = (TicketCharge.objects.filter(ticket=self.ticket)
                   .order_by("created"))

        outstanding = TicketCharge.outstanding_charges(
            charges, pluck="cost")

        return {
            'ticket': self.ticket,
            'ticket_updates': ticket_updates,
            'charges': charges,
            'charges_outstanding': sum(outstanding),
            'ticket_update_form': self.form,
            'cancel_form': forms.TicketCancelForm(),
            'mark_paid_form': forms.TicketPaidForm(),
            'close_form': forms.TicketCancelForm(),
            're_open_form': forms.TicketCancelForm(),
            'flag_form': forms.RequestFlagForm(),
            'file_upload_form': forms.DirectUploadForm(initial={
                "key":self.ticket.id,
                "redirect_to":'/request/%s/details' % self.ticket.id}),
            'charge_form': forms.RequestChargeForm()
        }

    #FIXME: AJAXize!
    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def post(self, request):
        print self.ticket
        form = forms.CommentForm(self.request.POST)

        if not form.is_valid():
            print "FORM WAS INVALID!!!"
            return self.get(request)

        comment = form.save(commit=False)
        print comment
        comment.ticket = self.ticket
        comment.author = request.user
        print "YAAY SAVING!!"
        comment.save()
        return HttpResponseRedirect(reverse('request_details', kwargs={ "ticket_id":self.ticket.id}))


class RemoveObjectHandler(TemplateView):
    GET_KEY = 'key'
    field_name = None

    not_found_message = _("The specified object could not be found.")
    not_attached_message = _("The specified object is not attached to"
                             " this ticket.")
    success_message = _("The specified object was successfully removed.")

    def get_obj(self, obj_key):
        raise NotImplementedError("get_obj not implemented")

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def _get(self, ticket_id=None):
        ticket = models.Ticket.get_by_id(int(ticket_id))
        obj_key = self.request.get(self.GET_KEY)

        obj = self.get_obj(obj_key)
        if not obj:
            self.add_message(self.not_found_message, 'error')

        obj_list = getattr(ticket, self.field_name, [])
        if obj not in obj_list:
            self.add_message(_(self.not_attached_message), 'warning')
        else:
            obj_list.remove(obj)
            ticket.put()
            self.add_message(_(self.success_message), 'success')

        return self.redirect(self.uri_for(
            'request_details', ticket_id=ticket_id))


class RequestDetailsActionHandler(JSONResponseMixin, TemplateView):
    """
    Base class for actions such as Cancel / Close / Etc from fragments to
    inherit from
    """

    form_class = None

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def get_context(self, ticket_id=None):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        ticket = models.Ticket.get_by_id(int(ticket_id))
        form = self.form_class(self.request.POST)
        not_allowed = not self.user_can(ticket)
        if form.validate() and not not_allowed:
            # save new update & add message
            self.form_valid(ticket, form)
        else:
            t = self.render_template('modals/form_basic.jinja', form=form,
                                     not_allowed=not_allowed)
            self.render_json_response({'status': 'error', 'html': t})



class RequestPaidHandler(RequestDetailsActionHandler):
    form_class = forms.TicketPaidForm

    def user_can(self, ticket):
        return self.profile.is_superuser or profile_in(self.profile, [ticket.responders])

    def form_valid(self, ticket, form):
        # mark all charges related to the ticket as being paid
        ticket.mark_charges_paid(form.paid_status.data)

        models.TicketUpdate(
            parent=ticket.key,
            ticket=ticket.key,
            author=self.profile.key,
            update_type=models.get_choice(
                _('Reconciled Charges'),
                models.TICKET_UPDATE_TYPES),
            comment=form.comment.data
        ).put()

        self.add_message(_('Request payment status has been updated.'))


class RequestAddChargeHandler(RequestDetailsActionHandler):
    form_class = forms.RequestChargeForm

    def user_can(self, ticket):
        return self.profile.is_superuser or profile_in(self.profile, [ticket.responders])

    def form_valid(self, ticket, form):
        charge = models.TicketCharge(
            parent=ticket.key,
            ticket=ticket.key,
            user=self.profile.key,
            item=form.item.data,
            cost=form.cost.data,
            cost_original_currency=form.cost_original_currency.data,
            original_currency=form.original_currency.data
        ).put()

        models.TicketUpdate(
            parent=ticket.key,
            ticket=ticket.key,
            author=self.profile.key,
            update_type=models.get_choice(
                _('Charge Added'),
                models.TICKET_UPDATE_TYPES),
            comment=form.comment.data,
            extra_relation=charge
        ).put()

        self.add_message(_('The new charge was added to the request.'))


class RequestReopenHandler(RequestDetailsActionHandler):
    form_class = forms.TicketCancelForm

    def user_can(self, ticket):
        return self.profile.is_superuser or profile_in(
            self.profile, [ticket.requester, ticket.responders])

    def form_valid(self, ticket, form):
        ticket.status = models.get_choice('In Progress', models.TICKET_STATUS)
        ticket.status_updated = datetime.datetime.now()
        ticket.put(comment=form.reason.data if hasattr(form, 'reason') else '')
        self.add_message(_('Request has been re-opened.'))


class RequestJoinHandler(RedirectView): #FIXME: Verify
    pattern_name = 'request_details'
    join_message = _("You have joined the ticket.")
    fail_message = _("You are already on the ticket.")

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def _get(self, ticket_id=None):
        ticket = models.Ticket.get_by_id(int(ticket_id))
        if ticket.join_user(self.profile):
            self.add_message(self.join_message, 'success')
        else:
            self.add_message(self.fail_message, 'warning')
        self.redirect(self.uri_for('request_details', ticket_id=ticket_id))


class RequestLeaveHandler(RedirectView): #FIXME: Verify
    pattern_name = 'request_details'
    leave_message = _("You are no longer part of this ticket.")

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def _get(self, ticket_id=None):
        ticket = models.Ticket.get_by_id(int(ticket_id))
        ticket.leave_user(self.profile)
        self.add_message(self.leave_message, 'success')
        self.redirect(self.uri_for('request_details', ticket_id=ticket_id))


class ResponseListHandler(TemplateView):
    template_name = "tickets/responds_list.jinja"
    """Display a list of tickets in which the logged in user should be
    responding to. """

    #FIXME: Auth
    #@role_in('staff', 'admin', 'volunteer')
    def get_context(self):
        tickets_to_respond = models.Ticket.query().filter(ndb.OR(
            models.Ticket.responders == self.profile.key,
            models.Ticket.volunteers == self.profile.key
        )).fetch()
        open_tickets, closed_tickets = split_open_tickets(tickets_to_respond)
        return {
            'requests': open_tickets,
            'closed_requests': closed_tickets
        }


class PublicListHandler(TemplateView):
    template_name = "tickets/public_list.jinja"
    """ Display a list of tickets which are open for volunteers to
    collaborate on.

    Only list open tickets so they can be picked up by volunteer users.
    """

    #FIXME: Auth
    #@role_in('user', 'staff', 'admin', 'volunteer')
    def get_context(self):
        public_tickets = models.Ticket.query().filter(
            models.Ticket.is_public == True,
            models.Ticket.status.IN(models.OPEN_TICKET_STATUSES)).fetch()
        open_tickets, closed_tickets = split_open_tickets(public_tickets)
        return {
            'requests': open_tickets,
            'closed_requests': closed_tickets
        }


class AdminTicketListTemplateView(TemplateView):

    """ Administrator views a list of all tickets in the system. Can view them
    by hotness (been open, need closing)
    """
    template_name = None
    object_name = 'tickets'

    #FIXME: Auth
    #@role_in('admin')
    def _get(self):
        direction = self.request.get('dir', 'next')
        cursor = Cursor(urlsafe=self.request.get('curs'))

        tickets, next_cursor, more = (self.get_queryset()
                                      .order(*self.get_order())
                                      .fetch_page(15, start_cursor=cursor))

        if direction == 'next':
            next_page_cursor = next_cursor
            previous_page_cursor = cursor.reversed()
        else:
            next_page_cursor = cursor.reversed()
            previous_page_cursor = next_cursor
            tickets.reverse()

        tickets = self.post_filter(tickets)

        context = {
            self.object_name: tickets,
            'next_cursor': next_page_cursor,
            'prev_cursor': previous_page_cursor,
            'more_results': more,
            'current_direction': direction
        }
        context.update(self.get_extra_context())
        self.render_response(self.template, **context)

    def post_filter(self, tickets):
        return tickets

    def get_extra_context(self):
        return {}


class AdminChargeReconcileInlineHandler(JSONResponseMixin, TemplateView):

    def get_object(self, charge_key):
        return ndb.Key(urlsafe=charge_key).get()

    def get_form(self):
        return forms.TicketChargeReconcileForm(self.request.POST, instance=self.charge)

    def render_form(self, form):
        return self.render_template('tickets/admin/reconcile_inline.jinja',
            reconcile_form=form,
            form_action=self.request.url,
            charge=self.charge)

    #FIXME: Auth
    #@role_in('admin')
    def _get(self, charge_key=None, status='success'):
        self.charge = self.get_object(charge_key)
        form = self.get_form()
        t = self.render_form(self.get_form())
        self.render_json_response({'status': status, 'html': t})

    #FIXME: Auth
    #@role_in('admin')
    def post(self, charge_key=None):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.charge = self.get_object(charge_key)
        form = self.get_form()

        if form.validate():
            form.save()
            self.add_message(_('Charge successfully reconciled.'), 'success')
            self.render_json_response({'status': 'success', 'data': self.charge.key.urlsafe()})
        else:
            t = self.render_form(form)
            self.render_json_response({'status': 'error', 'html': t})


class AdminCustomerChargesHandler(AdminTicketListTemplateView):
    object_name = 'charges'
    template_name = 'tickets/admin/admin_charges_customer.jinja'

    #FIXME: Auth
    #@role_in('admin')
    def dispatch(self, *args, **kwargs):
        self.customer = None

        customer_key = self.request.GET.get('user')
        if customer_key:
            self.customer = get_user_model().objects.get(id=customer_key)

        return super(AdminCustomerChargesHandler, self).dispatch(*args, **kwargs)

    def get_context_data(self):
        r = super(AdminCustomerChargesHandler, self).get_context_data()
        r['filter_form'] = forms.UserFilterForm(initial={"user":self.customer})
        return r

    def get_queryset(self):
        if self.customer:
            return models.TicketCharge.query().filter(
                models.TicketCharge.user==self.customer)
        else:
            return models.TicketCharge.query()

    def get_order(self):
        if self.request.get('dir', 'next') == 'next':
            return [-models.TicketCharge.created, models.TicketCharge.key]
        else:
            return [models.TicketCharge.created, -models.TicketCharge.key]

    def post_filter(self, objects):
        """
        bust the list cache by manually fetching the key which was modified
        in the last request via bypassing memcache and re-populating the record.
        """

        filtered = []
        data = self.request.get('data')
        if data:
            for o in objects:
                if o.key.urlsafe() == data:
                    filtered.append(ndb.Key(urlsafe=data).get(use_cache=False))
                else:
                    filtered.append(o)
        else:
            filtered = objects

        return filtered


class AdminOutstandingChargesHandler(AdminTicketListTemplateView):
    object_name = 'charges'
    template_name = 'tickets/admin/admin_charges_outstanding.jinja'

    def get_queryset(self):
        return models.TicketCharge.query().filter(
            models.TicketCharge.reconciled==False)

    def get_order(self):
        if self.request.get('dir', 'next') == 'next':
            return [-models.TicketCharge.created, models.TicketCharge.key]
        else:
            return [models.TicketCharge.created, -models.TicketCharge.key]

    def post_filter(self, objects):
        """
        Since ndb will cache the objects that we're filtering on, we need to
        manually prune out the reconciled charge from the object list.
        """
        data = self.request.get('data')
        if data:
            return [o for o in objects if o.key.urlsafe() != data]
        else:
            return objects


class AdminDeadlineTicketsHandler(AdminTicketListTemplateView):
    template_name = 'tickets/admin/admin_deadline.jinja'
    get_queryset = lambda _: (models.Ticket.query()
                              .filter(models.Ticket.status.IN(models.OPEN_TICKET_STATUSES)))

    def get_order(self):
        if self.request.get('dir', 'next') == 'next':
            return [models.Ticket.deadline, models.Ticket.key]
        else:
            return [-models.Ticket.deadline, -models.Ticket.key]


class AdminUnassignedTicketsHandler(AdminTicketListTemplateView):
    template_name = 'tickets/admin/admin_unassigned.jinja'
    get_queryset = lambda _: (models.Ticket.query()
                              .filter(models.Ticket.responders_len == 0)
                              .filter(
                                  models.Ticket.status.IN(['new', 'in-progress']))
        )

    def get_order(self):
        if self.request.get('dir', 'next') == 'next':
            return [-models.Ticket.created, models.Ticket.key]
        else:
            return [models.Ticket.created, -models.Ticket.key]


class AdminFlaggedTicketsHandler(AdminTicketListTemplateView):
    template_name = 'tickets/admin/admin_flagged.jinja'
    get_queryset = lambda _: (models.Ticket.query()
                              .filter(models.Ticket.flagged == True))

    def get_order(self):
        if self.request.get('dir', 'next') == 'next':
            return [models.Ticket.deadline]
        else:
            return [-models.Ticket.deadline]


class AdminHistoryTicketsHandler(AdminTicketListTemplateView):
    template_name = 'tickets/admin/admin_history.jinja'
    get_queryset = lambda _: (models.Ticket.query()
                              .filter(models.Ticket.status.IN(models.CLOSED_TICKET_STATUSES)))

    def get_order(self):
        if self.request.get('dir', 'next') == 'next':
            return [models.Ticket.created, models.Ticket.key]
        else:
            return [-models.Ticket.created, -models.Ticket.key]


class AdminSettingsHandler(JSONResponseMixin, TemplateView):
    template_name = "modals/form_basic.jinja"
    """
    Administrator edits a ticket's properties (re-assignment, closing, etc)
    """
    def dispatch(self):
        ticket = None
        if 'ticket_id' in self.kwargs:
            ticket_id = self.kwargs['ticket_id']
            ticket = models.Ticket.get_by_id(int(ticket_id))
        self.form = forms.AdminTicketSettingsForm(self.request.POST,
                                                  instance=ticket)
        super(AdminSettingsHandler, self).dispatch()

    #FIXME: Auth
    #@role_in('admin')
    def _get(self, ticket_id, status='success'):
        t = self.render_template('modals/form_basic.jinja',
                                 form=self.form,
                                 form_action=self.request.url)
        self.render_json_response({'status': status, 'html': t})

    #FIXME: Auth
    #@role_in('admin')
    def post(self, ticket_id):
        self.response.headers.add_header("Access-Control-Allow-Origin", "*")
        if self.form.validate():
            self.form.save()
            self.add_message(_('Ticket successfully saved.'))
        else:
            self.get(ticket_id, 'error')


class RequestMailHandler(object): #FIXME
    """
    Mail Handler receiver based on google's inbound mail handler.

    It accepts emails routed to notifications+<pk_match>@xxxx.appspotmail.com
    and creates a ticket update with the following map:
        - author: email sender
        - ticket: pk in +email address extension
        - type: 'update'
        - comment: plaintext email body
    """

    EMAIL_RE_MATCH = 'key'
    EMAIL_RE = "notification\+(?P<%s>[0-9]+)@.*\.appspotmail\.com" % EMAIL_RE_MATCH

    DEFAULT_ENCODING = "text/plain"

    def receive(self, msg):
        ticket = self.get_ticket(msg)
        profile = self.get_profile(msg)

        if ticket and profile:
            models.TicketUpdate(
                parent=ticket.key,
                ticket=ticket.key,
                author=profile.key,
                update_type=models.get_choice('Updated',
                    models.TICKET_UPDATE_TYPES),
                comment=self.drain_body(msg)
            ).put()

    def parse_address_key(self, msg):
        # to could be a list, and we need to test each to address for a
        # matching notification reply.
        if isinstance(msg.to, list):
            to_addresses = getaddresses(msg.to)
        else:
            to_addresses = getaddresses([msg.to])

        for name, addr in to_addresses:
            key_match = re.match(self.EMAIL_RE, addr)
            if not key_match or not self.EMAIL_RE_MATCH in key_match.groupdict():
                continue

            key = key_match.groupdict().get(self.EMAIL_RE_MATCH, None)
            if key:
                return key

        # no match could be found.
        return None

    def get_ticket(self, msg):
        key = self.parse_address_key(msg)
        if not key:
            return None

        ticket = models.Ticket.get_by_id(int(key))
        if not ticket:
            logging.info("Received reply to invalid ticket %s from address: %s"
                         % (key, msg.to))

        return ticket

    def get_profile(self, msg):
        name, addr = parseaddr(msg.sender)

        profile = models.UserProfile.query(
            models.UserProfile.email == addr).get()

        if not profile:
            logging.info("No email found for %s sent to: %s"
                         % (msg.sender, msg.to))

        return profile

    def drain_body(self, msg, encoding=None):
        # build a full body based on the text content of the email.
        # we assume that mail clients are nice enough to send the text content
        # of emails, rather than just html for simplification.
        encoding = self.DEFAULT_ENCODING if not encoding else encoding

        body_parts = []
        for ct, bdy in msg.bodies(encoding):
            body_parts.append(bdy.decode())
        full_body = '\n'.join(body_parts)
        return EmailReplyParser.parse_reply(full_body)


class Select2AllHandler(View, JSONResponseMixin):
    def get_context_data(self):
        return get_user_model().objects.all()




