from django.views.generic import DetailView, UpdateView, RedirectView
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404


class UserAccessMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        user_pk = kwargs.get("pk")
        if request.user.is_authenticated and not request.user.pk == user_pk:
            raise Http404
        return super().dispatch(request, *args, **kwargs)


class MyUserView(RedirectView):
    pattern_name = "user"

    def get_redirect_url(self, *args, **kwargs):
        pk = self.request.user.pk
        return super().get_redirect_url(*args, pk=pk, **kwargs)


class UserDetailView(UserAccessMixin, DetailView):
    model = get_user_model()
    template_name = "components/user/user_detail.html"
    context_object_name = "user"


class UserUpdateView(UserAccessMixin, UpdateView):
    model = get_user_model()
    template_name = "components/user/user_edit.html"
    context_object_name = "user"
