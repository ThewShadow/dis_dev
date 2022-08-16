from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.generic.base import ContextMixin, View


class ReportView(ContextMixin, View):
    paginate_by = 10
    model = None
    template_name = f'main/report_{model}.html'

    def get(self, request):
        queryset = self.get_queryset()
        show = self.define_number_to_show(len(queryset))
        page_number = self.get_page_number()
        page_obj = self.paginate(queryset, show, page_number)

        context = self.get_context_data()
        context['count_obj'] = queryset.count()
        context['page_obj'] = page_obj
        context['show_pages'] = show
        context['current_page'] = page_number
        context['pages_count'] = range(1, page_obj.paginator.num_pages + 1)
        context['query_string'] = request.GET.get('q', '')
        context['start_objects'] = (show * page_obj.number + 1) - show
        context['end_objects'] = (show * page_obj.number - show) + len(page_obj.object_list)

        response = render(request, self.template_name, context)

        response.set_cookie(key='current_page', value=page_number)
        response.set_cookie(key='show', value=show)

        return response

    def define_number_to_show(self, list_count):
        show = self.paginate_by
        if self.request.GET.get('show'):
            show = self.request.GET.get('show')
        elif self.request.COOKIES.get('show'):
            show = self.request.COOKIES.get('show')

        if not isinstance(show, int):
            try:
                show = int(show)
            except ValueError:
                show = self.paginate_by
        if show > list_count:
            show = list_count
        return show

    def get_page_number(self):
        page_number = self.request.GET.get('page')
        if page_number:
            return page_number
        else:
            return self.request.COOKIES.get('current_page', 1)

    def paginate(self, queryset, show_elements, page_number):
        if not queryset:
            return []
        else:
            return Paginator(queryset, show_elements).get_page(page_number)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        return context
