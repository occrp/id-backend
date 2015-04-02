#
#  THIS FILE IS OBSOLETE
#  EVERYTHING OF VALUE SHOULD BE REMOVED FROM IT
#
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




