from django.views.generic import CreateView

from .models import Budget
from .forms import BudgetForm


class Budgets(CreateView):
    form_class = BudgetForm
    template_name = "manage/budgets.jinja"
    success_url = '/manage/budgets'

    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Budget.objects.all()
        return super(CreateView, self).get_context_data(**kwargs)
