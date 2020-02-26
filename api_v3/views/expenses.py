from rest_framework import exceptions, mixins, serializers, viewsets

from api_v3.models import Action, Expense, Ticket
from api_v3.serializers import ExpenseSerializer
from .support import JSONApiEndpoint


class ExpensesEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        queryset = super(ExpensesEndpoint, self).get_queryset()

        if self.request.user.is_superuser:
            return queryset

        # If this is anonymous, for some reason DRF evaluates the
        # authentication after the queryset
        if not self.request.user.is_active:
            return queryset.none()

        return Expense.filter_by_user(self.request.user, queryset)

    def perform_create(self, serializer):
        """Make sure every new expense is linked to current user."""
        ticket = Ticket.objects.filter(
            responder_users=self.request.user,
            id=getattr(serializer.validated_data['ticket'], 'id', None)
        ).first()

        if not ticket and not self.request.user.is_superuser:
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )
        else:
            expense = serializer.save(user=self.request.user)

            Action.objects.create(
                action=expense,
                target=expense.ticket,
                actor=self.request.user,
                verb=self.action_name()
            )

            return expense

    def perform_update(self, serializer):
        """Allow only super users and ticket responders to update the expense"""
        expense = serializer.instance

        if (not self.request.user.is_superuser) and (
            self.request.user not in expense.ticket.responder_users.all()
        ):
            raise exceptions.NotFound()

        expense = serializer.save()

        Action.objects.create(
            action=expense,
            target=expense.ticket,
            actor=self.request.user,
            verb=self.action_name()
        )

        return expense
