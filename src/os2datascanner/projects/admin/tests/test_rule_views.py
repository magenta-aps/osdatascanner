from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

from ..adminapp.views.rule_views import RuleCreate


class RuleViewsTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.kjeld = get_user_model().objects.create_user(
                username='kjeld', email='kjeld@jensen.com', password='top_secret')

    def test_create_form_adds_authenthication_fields(self):
        """Tests whether authentication is properly added in a rule form"""
        create_view = RuleCreate()
        request = self.factory.post('/rules/regex/add/')
        request.user = self.kjeld
        create_view.setup(request)

        create_form = create_view.get_form()
        self.assertTrue('name' in create_form)
