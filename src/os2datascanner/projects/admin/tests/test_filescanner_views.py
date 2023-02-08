from django.test import TestCase
from django.urls import reverse_lazy
from django.contrib.auth.models import User


from ..core.models.client import Client
# from ..core.models.administrator import Administrator
from ..organizations.models import Organization
from ..adminapp.models.rules.rule import Rule
from ..adminapp.models.scannerjobs.filescanner import FileScanner


class FileScannerListViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="name", password="secret")
        self.client.force_login(self.user)
        self.client1 = Client.objects.create(name="Client1")
        self.organization1 = Organization.objects.create(
            name="Org1", slug="org1", client=self.client1)
        self.client2 = Client.objects.create(name="Client2")
        self.organization2 = Organization.objects.create(
            name="Org2", slug="org2", client=self.client2)

        self.filescanner1 = FileScanner.objects.create(
            name="Filescanner1", organization=self.organization1, unc="/root/folder")
        self.filescanner2 = FileScanner.objects.create(
            name="Filescanner2", organization=self.organization2, unc="/main/mappe")

        self.rule1 = Rule.objects.create(name="Rule1", organization=self.organization1)
        self.rule2 = Rule.objects.create(name="Rule2", organization=self.organization2)

        self.filescanner1.rules.add(self.rule1)
        self.filescanner2.rules.add(self.rule2)

    def test_superuser_list(self):
        """A superuser should be able to see all filescanners of all clients"""
        self.user.is_superuser = True
        self.user.save()

        url = reverse_lazy("filescanners")

        response = self.client.get(url)

        print(self.filescanner1)

        self.assertIn(self.filescanner1, response.get("object_list"))
        self.assertIn(self.filescanner2, response.get("object_list"))
