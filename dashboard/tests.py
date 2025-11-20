from django.test import TestCase, Client
from django.contrib.auth.models import User as AuthUser
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import Doctor, User, Appointment, Room
from .views import dashboard_stats
import uuid
from datetime import datetime

class DoctorModelTest(TestCase):
    def test_doctor_str_representation(self):
        """Test Doctor model string representation"""
        doctor = Doctor(
            name="John",
            surname="Smith",
            specialization="Cardiology"
        )
        self.assertEqual(str(doctor), "Dr. John Smith - Cardiology")
    
    def test_doctor_fields(self):
        """Test Doctor model fields"""
        doctor = Doctor(
            name="Jane",
            surname="Doe",
            age=35,
            specialization="Neurology",
            category="Senior",
            experience_years=10
        )
        self.assertEqual(doctor.name, "Jane")
        self.assertEqual(doctor.specialization, "Neurology")
        self.assertEqual(doctor.experience_years, 10)

class UserModelTest(TestCase):
    def test_user_str_representation(self):
        """Test User model string representation"""
        user = User(
            name="Alice",
            surname="Johnson",
            email="alice@example.com"
        )
        self.assertEqual(str(user), "Alice Johnson (alice@example.com)")
    
    def test_user_default_values(self):
        """Test User model default values"""
        user = User(name="Bob", surname="Wilson", email="bob@test.com")
        self.assertEqual(user.role, "user")
        self.assertFalse(user.disabled)

class AppointmentModelTest(TestCase):
    def test_appointment_str_representation(self):
        """Test Appointment model string representation"""
        appointment = Appointment(
            datetime=datetime(2024, 1, 15, 10, 30)
        )
        self.assertEqual(str(appointment), "Appointment 2024-01-15 10:30")
    
    @patch('dashboard.models.Doctor.objects.get')
    def test_get_doctor_success(self, mock_get):
        """Test successful doctor retrieval"""
        mock_doctor = MagicMock()
        mock_get.return_value = mock_doctor
        
        appointment = Appointment(doctor_id=uuid.uuid4())
        result = appointment.get_doctor()
        
        self.assertEqual(result, mock_doctor)
    
    @patch('dashboard.models.Doctor.objects.get')
    def test_get_doctor_not_found(self, mock_get):
        """Test doctor not found"""
        from dashboard.models import Doctor
        mock_get.side_effect = Doctor.DoesNotExist
        
        appointment = Appointment(doctor_id=uuid.uuid4())
        result = appointment.get_doctor()
        
        self.assertIsNone(result)

class DashboardViewTest(TestCase):
    def setUp(self):
        """Set up test user and client"""
        self.client = Client()
        self.staff_user = AuthUser.objects.create_user(
            username='staff',
            password='testpass',
            is_staff=True
        )
    
    @patch('dashboard.views.Doctor.objects')
    @patch('dashboard.views.User.objects')
    @patch('dashboard.views.Appointment.objects')
    @patch('dashboard.views.Room.objects')
    def test_dashboard_stats_view(self, mock_rooms, mock_appointments, mock_users, mock_doctors):
        """Test dashboard stats view with mocked data"""
        # Mock return values
        mock_doctors.count.return_value = 5
        mock_users.filter.return_value.count.return_value = 20
        mock_appointments.count.return_value = 15
        mock_appointments.filter.return_value.count.return_value = 3
        mock_rooms.count.return_value = 8
        mock_doctors.values.return_value.annotate.return_value.order_by.return_value = []
        
        # Login as staff user
        self.client.login(username='staff', password='testpass')
        
        # Make request
        response = self.client.get('/dashboard/stats/')
        
        # Check response
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_requires_staff(self):
        """Test that dashboard requires staff permissions"""
        # Create regular user
        regular_user = AuthUser.objects.create_user(
            username='regular',
            password='testpass',
            is_staff=False
        )
        
        # Try to access without login
        response = self.client.get('/dashboard/stats/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
        # Try to access as regular user
        self.client.login(username='regular', password='testpass')
        response = self.client.get('/dashboard/stats/')
        self.assertEqual(response.status_code, 302)  # Redirect (no staff access)

class RoomModelTest(TestCase):
    def test_room_str_representation(self):
        """Test Room model string representation"""
        room = Room(number=101)
        self.assertEqual(str(room), "Room 101")
