from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect

from . import models
from .utils import in_res_admin_group, can_modify_application, can_view_application, can_modify_achievement, can_view_achievement


class ResSubBasicMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        if self.request.user.id:
            return True

    def dispatch(self, request, *args, **kwargs):
        user_test_result = self.get_test_func()()
        if not user_test_result and self.request.user.is_authenticated:
            return HttpResponseRedirect('/accounts/denied/?app=res')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_admin"] = in_res_admin_group(self.request.user)
        return context


class LoginAccessRequiredMixin(ResSubBasicMixin):
    pass


class ResAdminRequiredMixin(ResSubBasicMixin):
    def test_func(self):
        return in_res_admin_group(self.request.user)


class CanModifyApplicationRequiredMixin(ResSubBasicMixin):
    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        application_id = None
        try:
            obj = self.get_object()
            if isinstance(obj, models.Application):
                application_id = obj.id
            # elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestFile):
            #     request_id = obj.csas_request_id

        except AttributeError:
            pass
            if self.kwargs.get("application"):
                application_id = self.kwargs.get("application")

        finally:
            if application_id:
                return can_modify_application(self.request.user, application_id)


class CanViewApplicationRequiredMixin(ResSubBasicMixin):
    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        application_id = None
        try:
            obj = self.get_object()
            if isinstance(obj, models.Application):
                application_id = obj.id
            # elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestFile):
            #     request_id = obj.csas_request_id

        except AttributeError:
            pass
            if self.kwargs.get("application"):
                application_id = self.kwargs.get("application")

        finally:
            if application_id:
                return can_view_application(self.request.user, application_id)


class CanModifyAchievementRequiredMixin(ResSubBasicMixin):
    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        achievement_id = None
        try:
            obj = self.get_object()
            if isinstance(obj, models.Achievement):
                achievement_id = obj.id
            # elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestFile):
            #     request_id = obj.csas_request_id

        except AttributeError:
            pass
            if self.kwargs.get("achievement"):
                achievement_id = self.kwargs.get("achievement")

        finally:
            if achievement_id:
                return can_modify_achievement(self.request.user, achievement_id)


class CanViewAchievementRequiredMixin(ResSubBasicMixin):
    def test_func(self):
        # the assumption is that either we are passing in a Project object or an object that has a project as an attribute
        achievement_id = None
        try:
            obj = self.get_object()
            if isinstance(obj, models.Achievement):
                achievement_id = obj.id
            # elif isinstance(obj, models.CSASRequestReview) or isinstance(obj, models.CSASRequestFile):
            #     request_id = obj.csas_request_id

        except AttributeError:
            pass
            if self.kwargs.get("achievement"):
                achievement_id = self.kwargs.get("achievement")

        finally:
            if achievement_id:
                return can_view_achievement(self.request.user, achievement_id)


class SuperuserOrAdminRequiredMixin(ResSubBasicMixin):

    def test_func(self):
        return self.request.user.is_superuser or in_res_admin_group(self.request.user)
