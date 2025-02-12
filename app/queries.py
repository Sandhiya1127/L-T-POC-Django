from app.models import lt_july_01_final_data_12_hours
from django.db.models import Count, Max, Sum, F, Value, Case, When, CharField
from django.db.models.functions import Concat

from app.models import lt_july_01_final_data_12_hours
from django.db.models import Count, Max, Sum, F, Value, Case, When, CharField
from django.db.models.functions import Concat

# 🔹 Function to get workforce data
def get_all_workforce_data():
    return lt_july_01_final_data_12_hours.objects.filter(duplicate=False).annotate(
        labour_count=Count(Case(When(object_name="labour", then=1))),
        group_talking=Max('group_talking'),
        idle=Max('idle'),
        no_helmet=Max('no_helmet'),
        date_time=Concat(F('date'), Value(' '), F('time'), output_field=CharField())
    ).order_by('date', 'time')


def get_workforce_activity():
    return lt_july_01_final_data_12_hours.objects.filter(duplicate=False).annotate(
        labour_count=Count(Case(When(object_name="labour", then=1)))
    ).values('time', 'labour_count').order_by('date', 'time')


from django.db import connection
from django.db import connection

def get_workforce_idle(date_filter=None, group_talking_filter=None):
    query = """
    WITH dates AS (
        SELECT 
            date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
        FROM 
            generate_series(1, 1) AS n
    ),
    numbers AS (
        SELECT time_g, left(right(time_g::varchar,8),5) time_g_t
        FROM generate_series
            ('2024-07-01'::timestamp, '2024-07-02'::timestamp, '5 minutes'::interval) time_g
        WHERE date(time_g) <> '2024-07-02'
    )
    SELECT a.time_g_t,
           COALESCE(b.labour_count, 0) AS labour_count,
           b.idle,
           b.group_event,
           a.date::text,
           b.no_helmet,
           file_name AS img,
           SUM(labour_time) AS labour_time
    FROM 
        (SELECT d.date::date AS date,
                n.time_g AS time,
                time_g_t
         FROM dates d
         CROSS JOIN numbers n) a
    LEFT JOIN (
        SELECT LEFT(time::varchar,5) AS time,
               COALESCE(labour_count, 0) AS labour_count,
               MAX(idle) AS idle,
               MAX(group_event) AS group_event,
               MAX("date"::varchar) AS "date",
               no_helmet,
               file_name,
               SUM(labour_time) AS labour_time
        FROM (
            SELECT activity, milestone,
                   SUM(CASE WHEN object_name = 'labour' THEN 1 ELSE 0 END) AS labour_count,
                   SUM(CASE WHEN object_name = 'labour' THEN 10 ELSE 0 END) AS labour_time,
                   object_name, channel, MAX("date")::varchar AS "date",
                   CAST(time AS varchar) AS time,
                   CASE WHEN MAX(idle) = 'true' OR MAX(group_event) = 'true' THEN file_name END AS file_name,
                   MAX(group_event) AS group_event,
                   MAX(idle) AS idle,
                   MAX(no_helmet) AS no_helmet,
                   CONCAT(CAST(date AS varchar), ' ', CAST(time AS varchar)) AS date_time,
                   SUM(group_count) AS group_count,
                   SUM(idle_count) AS idle_count,
                   MAX(no_helmet_count) AS no_helmet_count,
                   MAX(no_vest) AS no_vest,
                   MAX(no_vest_count) AS no_vest_count,
                   ARRAY_AGG(box_coordinates) AS box_coordinates
            FROM public.lt_july_01_final_data_12_hours
            WHERE duplicate IS NULL 
              AND (object_name = 'labour' OR class_id IS NULL)
              AND confidence_score >= 0.6
            {date_condition}
            {group_talking_condition}
            GROUP BY object_name, channel, date, "time", file_name, activity, milestone
        ) a
        GROUP BY date_part('hour', CONCAT("date",' ',"time")::timestamp), "date",
                 floor(date_part('minutes', CONCAT("date",' ',"time")::timestamp) / 5) * 5
    ) b ON a."date"::varchar = b."date"::varchar AND a.time_g_t = b."time"
    GROUP BY a.time_g_t, 
             COALESCE(b.labour_count, 0),
             b.idle,
             b.group_event,
             a.date,
             b.no_helmet,
             file_name
    ORDER BY a."date", 1
    """
    
    if date_filter:
        query = query.replace("{date_condition}", f"AND date = '{date_filter}'")
    else:
        query = query.replace("{date_condition}", "")
        
    if group_talking_filter:
        query = query.replace("{group_talking_condition}", f"AND group_talking = '{group_talking_filter}'")
    else:
        query = query.replace("{group_talking_condition}", "")
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
    
    data = [
        {
            'time': row[0],
            'labour_count': row[1],
            'idle': row[2],
            'group_event': row[3],
            'date': row[4],
            'no_helmet': row[5],
            'img': row[6],
            'labour_time': row[7]
        }
        for row in result
    ]
    return data

def get_group_talking_events():
    return lt_july_01_final_data_12_hours.objects.filter(group_talking=True).annotate(
        total_count=Count('id')
    ).values('activity', 'milestone', 'total_count').order_by('-date', '-time')

def get_idle_events():
    return lt_july_01_final_data_12_hours.objects.filter(idle=True).annotate(
        total_count=Count('id')
    ).values('activity', 'milestone', 'total_count').order_by('-date', '-time')


def get_no_helmet_events():
    return lt_july_01_final_data_12_hours.objects.filter(no_helmet=True).annotate(
        total_count=Count('id')
    ).values('activity', 'milestone', 'total_count').order_by('-date', '-time')

def get_pie_chart_data():
    total_time = lt_july_01_final_data_12_hours.objects.aggregate(total_time=Sum('labour_time'))['total_time'] or 1

    data = lt_july_01_final_data_12_hours.objects.aggregate(
        active=Sum('labour_time') - (Sum('idle_count') + Sum('group_count')),
        idle=Sum('idle_count'),
        group=Sum('group_count')
    )

    return [
        {'name': 'Active', 'value': round((data['active'] / total_time) * 100, 2) if total_time else 0},
        {'name': 'Idle', 'value': round((data['idle'] / total_time) * 100, 2) if total_time else 0},
        {'name': 'Group', 'value': round((data['group'] / total_time) * 100, 2) if total_time else 0}
    ]

def get_pier_progress():
    return lt_july_01_final_data_12_hours.objects.values(
        'activity', 'milestone'
    ).annotate(
        labour_count=Sum('labour_time'),
        working_hours=Sum('labour_time') / 60 / 60,  # Convert seconds to hours
        active_hours=Sum('active_hours'),
        inactive_hours=Sum('inactive_hours'),
        total_planned_hours=Sum('total_planned_hrs'),
        day_count=Count('date'),
        delay_status=Case(
            When(day_count__gt=3, then=Value('Delay')),
            default=Value('On Time'),
            output_field=CharField()
        )
    ).order_by('milestone')

