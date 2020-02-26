from rest_framework_json_api import serializers

from api_v3.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):

    included_serializers = {
        'user': 'api_v3.serializers.ProfileSerializer',
        'ticket': 'api_v3.serializers.TicketSerializer'
    }

    class Meta:
        model = Expense
        read_only_fields = ('user', 'updated_at')
        fields = (
            'id',
            'user',
            'ticket',
            'amount',
            'amount_currency',
            'notes',
            'scope',
            'payment_method',
            'created_at',
            'updated_at'
        )
