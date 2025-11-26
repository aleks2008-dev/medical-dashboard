from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .models import Doctor
from datetime import datetime, timedelta


@staff_member_required
def dashboard_stats(request):
    """Dashboard with medical statistics"""
    from django.db import connection

    # Оптимизированный запрос для всех счетчиков одновременно
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM doctors) as total_doctors,
                (SELECT COUNT(*) FROM users WHERE role = 'user')
                    as total_patients,
                (SELECT COUNT(*) FROM appointments) as total_appointments,
                (SELECT COUNT(*) FROM rooms) as total_rooms,
                (SELECT COUNT(*) FROM appointments WHERE datetime >= %s)
                    as recent_appointments,
                (SELECT COUNT(*) FROM appointments WHERE DATE(datetime) = %s)
                    as today_appointments
        """,
            [datetime.now() - timedelta(days=7), datetime.now().date()],
        )

        row = cursor.fetchone()
        (
            total_doctors,
            total_patients,
            total_appointments,
            total_rooms,
            recent_appointments,
            today_appointments,
        ) = row

    # Popular specializations (оставляем ORM для читаемости)
    specializations = (
        Doctor.objects.values("specialization")
        .annotate(count=Count("specialization"))
        .order_by("-count")[:5]
    )

    context = {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_rooms": total_rooms,
        "recent_appointments": recent_appointments,
        "today_appointments": today_appointments,
        "specializations": specializations,
    }

    return render(request, "dashboard/stats.html", context)
