from rest_framework import exceptions, mixins, serializers, viewsets

from api_v3.models import Action, Expense, Ticket
from api_v3.serializers import ExpenseSerializer
from .support import JSONApiEndpoint


class ExpensesEndpoint(
        JSONApiEndpoint,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        mixins.UpdateModelMixin,
        viewsets.ReadOnlyModelViewSet):

    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    ordering_fields = ('created_at', 'updated_at')
    filter_fields = {
        'created_at': ['range'],
        'scope': ['exact'],
        'payment_method': ['exact'],
        'ticket': ['exact'],
        'user': ['exact']
    }

    def get_queryset(self):
        queryset = super(ExpensesEndpoint, self).get_queryset()

        if self.request.user.is_staff or self.request.user.is_superuser:
            return queryset

        return queryset.none()

    def perform_create(self, serializer):
        """Make sure every new expense is linked to current user."""
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise serializers.ValidationError(
                [{'data/attributes/ticket': 'Ticket not found.'}]
            )

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
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise exceptions.NotFound()

        return serializer.save()

    def perform_destroy(self, instance):
        """Make sure only super user or author can remove the expense."""
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            raise exceptions.NotFound()

        Action.objects.create(
            actor=self.request.user, target=instance.ticket,
            action=instance.user, verb=self.action_name())

        return instance.delete()
