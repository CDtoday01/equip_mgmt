# backend/tests/test_department_api.py
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from people.models import Department

@pytest.mark.django_db
class TestDepartmentAPI:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("department-list")  # 對應 DRF router 的 basename

    def test_create_department(self):
        data = {"name": "教務處"}
        response = self.client.post(self.url, data, format="json")

        assert response.status_code == 201
        assert Department.objects.filter(name="教務處").exists()

    def test_create_duplicate_department(self):
        Department.objects.create(name="學務處")
        data = {"name": "學務處"}
        response = self.client.post(self.url, data, format="json")

        # 預期應該回傳 400，因為 unique=True
        assert response.status_code == 400
        assert "name" in response.data

    def test_list_departments(self):
        Department.objects.create(name="總務處")
        response = self.client.get(self.url)

        assert response.status_code == 200
        assert any(dept["name"] == "總務處" for dept in response.data)
