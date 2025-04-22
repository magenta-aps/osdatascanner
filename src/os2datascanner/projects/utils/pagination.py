from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.utils.translation import gettext_lazy as _


class EmptyPagePaginator(Paginator):
    def validate_number(self, number):
        try:
            return super(EmptyPagePaginator, self).validate_number(number)
        except EmptyPage:
            if number > 1:
                return self.num_pages
            else:
                raise Http404(_('The page does not exist'))
