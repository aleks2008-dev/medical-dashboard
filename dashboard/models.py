from django.db import models
import uuid


class Doctor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.IntegerField()
    specialization = models.CharField(max_length=100)
    category = models.CharField(max_length=50)
    experience_years = models.IntegerField(default=0)

    class Meta:
        managed = False  # Django doesn't manage this table
        db_table = "doctors"

    def __str__(self):
        return f"Dr. {self.name} {self.surname} - {self.specialization}"


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField()
    age = models.IntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, default="user")
    disabled = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = "users"

    def __str__(self):
        return f"{self.name} {self.surname} ({self.email})"


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    number = models.IntegerField()

    class Meta:
        managed = False
        db_table = "rooms"

    def __str__(self):
        return f"Room {self.number}"


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    datetime = models.DateTimeField()
    doctor_id = models.UUIDField()
    user_id = models.UUIDField()
    room_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = "appointments"

    def __str__(self):
        return f"Appointment {self.datetime.strftime('%Y-%m-%d %H:%M')}"

    def get_doctor(self):
        try:
            return Doctor.objects.get(id=self.doctor_id)
        except Doctor.DoesNotExist:
            return None

    def get_patient(self):
        try:
            return User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            return None

    def get_room(self):
        try:
            return Room.objects.get(id=self.room_id)
        except Room.DoesNotExist:
            return None
