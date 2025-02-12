import json
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

import json
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import json
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({"error": "Username already taken"}, status=400)

            # ✅ Correct way to create a user (automatically hashes the password)
            user = User.objects.create_user(username=username, email=email, password=password)  
            user.save()

            return JsonResponse({"message": "User registered successfully"}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)

from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.shortcuts import render
import json

def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({"error": "Username and password are required"}, status=400)

            user = authenticate(request, username=username, password=password)  # Authenticate user
            if user is not None:
                auth_login(request, user)  # Log in the user
                return JsonResponse({"message": "Login successful", "redirect_url": "/configuration/"}, status=200)
            else:
                return JsonResponse({"error": "Invalid username or password"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def configuration(request):
    return render(request, 'configuration.html')

def insights(request):
    return render(request, 'insights.html')

from django.http import JsonResponse
from django.views import View
from app.queries import *

from django.http import JsonResponse
from django.views import View
from django.db import connection

class WorkforceDataView(View):
    def get(self, request):
        query = """
        SELECT activity, milestone, COUNT(CASE WHEN object_name = 'labour' THEN 1 END) AS labour_count,
        object_name, channel, CAST(date AS VARCHAR) AS date, CAST(time AS VARCHAR) AS time, file_name,
        processing_time, MAX(group_talking) AS group_talking, MAX(idle) AS idle, MAX(no_helmet) AS no_helmet,
        CONCAT(CAST(date AS VARCHAR), ' ', CAST(time AS VARCHAR)) AS date_time, SUM(group_count) AS group_count,
        SUM(idle_count) AS idle_count, MAX(no_helmet_count) AS no_helmet_count, MAX(no_vest) AS no_vest,
        MAX(no_vest_count) AS no_vest_count, ARRAY_AGG(box_coordinates) AS box_coordinates
        FROM public.app_lt_july_01_final_data_12_hours
        WHERE duplicate IS NULL AND (object_name = 'labour' OR class_id IS NULL)
        GROUP BY activity, milestone, object_name, channel, date, "time", file_name, processing_time
        ORDER BY date, "time", file_name
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]  # Get column names
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]  # Convert to dict
        
        return JsonResponse({'data': data}, safe=False)
    
from django.http import JsonResponse
from django.db import connection
from collections import defaultdict
import json

def get_data_time_series(request):
    with connection.cursor() as cursor:
        cursor.execute("""
        WITH dates AS (
    SELECT 
        date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
    FROM 
        generate_series(1, 5) AS n
),
numbers AS (
    SELECT 
        generate_series(0, 23) AS time
)
Select "time",
case when active_m = 0 then 0 else round(((inactive_m::float/active_m::float)*100)) end "value" ,
"date",labour_count,work_hour,active_hour,active_m,inactive_m
from (
select "time","value","date",labour_count,
case when labour_count = 0 then 0 else work_hour end work_hour,
case when labour_count = 0 then 0 else active_hour end active_hour,
case when active_m is null then FLOOR(RANDOM() * 180) else active_m end active_m,
case when labour_count = 0 then 0 else inactive_m end inactive_m,labour_time

from (
Select *,
	(labour_time/60)/60 work_hour,
	((labour_time/60) - ("value"/60))/60 active_hour,
round((labour_time - "value")/60) active_m,
round("value"/60) inactive_m
--case when inactive_minutes = 0 then 0 else round(((inactive_minutes::float/active_minutes::float)*100)) end perc
from (
select a."time"::int,
case when a."date" ='2024-07-01' then (case when b."value" is null then 0 else "value" end)::int else a.r_value end "value",
a."date"::varchar,
case when a."date" ='2024-07-01' then (case when b."labour_count" is null then 0 else "labour_count" end)::int else round(RANDOM() * 15) end "labour_count",
	labour_time
-- 	case when b.labour_count is null then 0 else b.labour_count * 3600 end work_hour,
-- case when b.labour_count is null then 0 else b.labour_count * 3600 end - (case when a."date" ='2024-07-01' then (case when b."value" is null then 0 else "value" end)::int else a.r_value end)  active_hour,
-- round((case when b.labour_count is null then 0 else b.labour_count * 3600 end - (case when a."date" ='2024-07-01' then (case when b."value" is null then 0 else "value" end)::int else a.r_value end))/60) active_minutes,
-- (case when b."value" is null then 0 else "value" end) /60 inactive_minutes
from (
SELECT 
    d.date::date date,
    n.time::int time,FLOOR(RANDOM() * 2600) r_value
FROM 
    dates d
CROSS JOIN 
    numbers n ) a
	left join (
Select "time"::int "time",(timeidle_seconds+timegrp_seconds)::int "value","date",labour_count,sum(labour_time::int) labour_time
-- labour_time_seconds,timeidle_seconds,timegrp_seconds,
-- case when labour_time_seconds = 0 then 0 else 
-- round(((sum(labour_time_seconds) - (sum(timeidle_seconds) + sum(timegrp_seconds)))/sum(labour_time_seconds))*100,2) end "value"
from (
Select left(time::varchar,2) time,case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,
case when timegrp is null then 0 else timegrp end timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,
	case when timeidle is null then 0 else timeidle end timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 case when labour_time is null then 0 else labour_time end labour_time
--   TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 300 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 300 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date"::varchar = c."date"::varchar and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,2),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a
group  by "date","time",timeidle_seconds,timegrp_seconds,labour_count )
b on a."date"::varchar = b."date"::varchar and a.time = b."time") a
	) a
	) a
order by 3,1
        """)
        
        result = cursor.fetchall()

    # ✅ Process the data into JSON
    data = defaultdict(list)
    for row in result:
        value = (row[0], row[1], row[3], row[4], row[5], row[6], row[7])  
        date = row[2]
        data[date].append(value)

    return JsonResponse(dict(data), safe=False)


import json
from collections import defaultdict
from django.http import JsonResponse
from django.db import connection
from django.views import View

# Helper function to execute raw SQL
def execute_raw_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return results

# Workforce Idle Data View
# class WorkforceIdleDataView(View):
#     def get(self, request):
#         idle_date = request.GET.get('idle_date', None)

#         if idle_date:
#             query = """ WITH dates AS (
#     SELECT 
#         date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
#     FROM 
#         generate_series(1, 1) AS n
# ),
# numbers AS (
#     SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
# FROM generate_series
#         ( '2024-07-01'::timestamp 
#         , '2024-07-02'::timestamp
#         , '5 minutes'::interval) time_g
# 	where date(time_g) <> '2024-07-02'
# )
# select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
# b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
# (SELECT 
#     d.date::date date,
#     n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
# FROM 
#     dates d
# CROSS JOIN 
#     numbers n ) a
# left join (
# 	Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
# max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
# 		select date_part('hour', concat("date",' ',"time")::timestamp),
# 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
# 		min("time") "time","date",
# 		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
# 	sum(labour_time) labour_time
# 		from (
# 				SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
# 			sum(case when object_name = 'labour' then 10 end) labour_time,
# 				object_name, channel, 
# 				max("date")::varchar "date",cast(time as varchar) time, 
# 			case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
# 				max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
# 				concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
# 				sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
# 				max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
# 				FROM public.app_lt_july_01_final_data_12_hours
# 				where duplicate is null and (object_name = 'labour' or class_id is null)
# 				and confidence_score >= 0.6
# 				group by object_name, channel, 
# 				date, "time", file_name, activity, milestone
# 			 )a
# 		group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
# 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
# 	) a
# group by left(time::varchar,5),labour_count,no_helmet,file_name
# )  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
# group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
# b.idle,b.group_event,a.date,b.no_helmet,file_name
# order by a."date",1
# """
# #             data = execute_raw_query(query, [idle_date])
# #         else:
#             query = """ WITH dates AS (
#     SELECT 
#         date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
#     FROM 
#         generate_series(1, 1) AS n
# ),
# numbers AS (
#     SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
# FROM generate_series
#         ( '2024-07-01'::timestamp 
#         , '2024-07-02'::timestamp
#         , '5 minutes'::interval) time_g
# 	where date(time_g) <> '2024-07-02'
# )
# select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
# b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
# (SELECT 
#     d.date::date date,
#     n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
# FROM 
#     dates d
# CROSS JOIN 
#     numbers n ) a
# left join (
# 	Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
# max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
# 		select date_part('hour', concat("date",' ',"time")::timestamp),
# 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
# 		min("time") "time","date",
# 		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
# 	sum(labour_time) labour_time
# 		from (
# 				SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
# 			sum(case when object_name = 'labour' then 10 end) labour_time,
# 				object_name, channel, 
# 				max("date")::varchar "date",cast(time as varchar) time, 
# 			case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
# 				max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
# 				concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
# 				sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
# 				max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
# 				FROM public.app_lt_july_01_final_data_12_hours
# 				where duplicate is null and (object_name = 'labour' or class_id is null)
# 			and confidence_score >= 0.6
# 				group by object_name, channel, 
# 				date, "time", file_name, activity, milestone
# 			 )a
# 		group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
# 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
# 	) a
# group by left(time::varchar,5),labour_count,no_helmet,file_name
# )  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
# group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
# b.idle,b.group_event,a.date,b.no_helmet,file_name

# order by a."date",1
# # """
#             data = execute_raw_query(query)
            
#             if not data:
#                return JsonResponse({"error": "No data found for the given date"}, status=404)


#         return JsonResponse(data, safe=False)

# # Workforce Time Series Data View
# class WorkforceTimeSeriesDataView(View):
#     def get(self, request):
#         query = """ YOUR SQL QUERY FOR query_time_series """
#         data = execute_raw_query(query)
#         return JsonResponse(data, safe=False)


class WorkforceIdleDataView(View):
    def get(self, request):
        idle_date = request.GET.get('idle_date', None)

        # Ensure 'data' is always initialized
        data = []

        try:
            if idle_date:
                query = """ WITH dates AS (
    SELECT 
        date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
    FROM 
        generate_series(1, 1) AS n
),
numbers AS (
    SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
FROM generate_series
        ( '2024-07-01'::timestamp 
        , '2024-07-02'::timestamp
        , '5 minutes'::interval) time_g
	where date(time_g) <> '2024-07-02'
)
select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
(SELECT 
    d.date::date date,
    n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
FROM 
    dates d
CROSS JOIN 
    numbers n ) a
left join (
	Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
	sum(labour_time) labour_time
		from (
				SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
			sum(case when object_name = 'labour' then 10 end) labour_time,
				object_name, channel, 
				max("date")::varchar "date",cast(time as varchar) time, 
			case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
				max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
				concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
				sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
				max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
				FROM public.app_lt_july_01_final_data_12_hours
				where duplicate is null and (object_name = 'labour' or class_id is null)
				and confidence_score >= 0.6
				group by object_name, channel, 
				date, "time", file_name, activity, milestone
			 )a
		group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
	) a
group by left(time::varchar,5),labour_count,no_helmet,file_name
)  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
b.idle,b.group_event,a.date,b.no_helmet,file_name
order by a."date",1"""  # Use the correct SQL query
                data = execute_raw_query(query, [idle_date])
            else:
                query = """ WITH dates AS (
    SELECT 
        date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
    FROM 
        generate_series(1, 1) AS n
),
numbers AS (
    SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
FROM generate_series
        ( '2024-07-01'::timestamp 
        , '2024-07-02'::timestamp
        , '5 minutes'::interval) time_g
	where date(time_g) <> '2024-07-02'
)
select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
(SELECT 
    d.date::date date,
    n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
FROM 
    dates d
CROSS JOIN 
    numbers n ) a
left join (
	Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
	sum(labour_time) labour_time
		from (
				SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
			sum(case when object_name = 'labour' then 10 end) labour_time,
				object_name, channel, 
				max("date")::varchar "date",cast(time as varchar) time, 
			case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
				max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
				concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
				sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
				max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
				FROM public.app_lt_july_01_final_data_12_hours
				where duplicate is null and (object_name = 'labour' or class_id is null)
			and confidence_score >= 0.6
				group by object_name, channel, 
				date, "time", file_name, activity, milestone
			 )a
		group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
	) a
group by left(time::varchar,5),labour_count,no_helmet,file_name
)  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
b.idle,b.group_event,a.date,b.no_helmet,file_name

order by a."date",1 """  # Another SQL query without idle_date
                data = execute_raw_query(query)

            print("Query Result:", data)  # Debugging

            if not data:  # Handle empty results
                return JsonResponse({"error": "No data available"}, status=404)

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)


from django.http import JsonResponse
from django.views import View
import json
from django.conf import settings

def execute_raw_query(query, params=None):
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


class WorkforceIdleDataWithDateView(View):
    def get(self, request):
        # idle_date = request.GET.get('idle_date')

        # if not idle_date:
        #     return JsonResponse({"error": "idle_date parameter is required"}, status=400)

        query = """ 
					WITH dates AS (
				SELECT 
					date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
				FROM 
					generate_series(1, 1) AS n
			),
			numbers AS (
				SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
			FROM generate_series
					( '2024-07-01'::timestamp 
					, '2024-07-02'::timestamp
					, '5 minutes'::interval) time_g
				where date(time_g) <> '2024-07-02'
			)
			select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
			b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
			(SELECT 
				d.date::date date,
				n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
			FROM 
				dates d
			CROSS JOIN 
				numbers n ) a
			left join (
				Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
			max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
					select date_part('hour', concat("date",' ',"time")::timestamp),
					floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
					min("time") "time","date",
					max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
				sum(labour_time) labour_time
					from (
							SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
						sum(case when object_name = 'labour' then 10 end) labour_time,
							object_name, channel, 
							max("date")::varchar "date",cast(time as varchar) time, 
						case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
							max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
							concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
							sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
							max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
							FROM public.app_lt_july_01_final_data_12_hours
							where duplicate is null and (object_name = 'labour' or class_id is null)
							and confidence_score >= 0.6
							group by object_name, channel, 
							date, "time", file_name, activity, milestone
						)a
					group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
					floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
				) a
			group by left(time::varchar,5),labour_count,no_helmet,file_name
			)  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
			group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
			b.idle,b.group_event,a.date,b.no_helmet,file_name
			order by a."date",1
        """
        
        try:
            data = execute_raw_query(query)

            # data = execute_raw_query(query, [idle_date])

            if not data:
                return JsonResponse({"error": "No data available"}, status=404)

            # for entry in data:
            #     if entry.get("img") and entry["img"].strip():  # Ensure file_name exists
            #         entry["img"] = f"{settings.MEDIA_URL}{entry['img']}".replace("//", "/")  # ✅ Remove double slashes
            #     else:
            #         entry["img"] = ""
					

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

            # return JsonResponse(data, safe=False)

        # except Exception as e:
        #     return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)
import json
from django.http import JsonResponse
from django.db import connection
from django.views import View

query_workforce_idle_date = """
    
					WITH dates AS (
				SELECT 
					date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
				FROM 
					generate_series(1, 1) AS n
			),
			numbers AS (
				SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
			FROM generate_series
					( '2024-07-01'::timestamp 
					, '2024-07-02'::timestamp
					, '5 minutes'::interval) time_g
				where date(time_g) <> '2024-07-02'
			)
			select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
			b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
			(SELECT 
				d.date::date date,
				n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
			FROM 
				dates d
			CROSS JOIN 
				numbers n ) a
			left join (
				Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
			max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
					select date_part('hour', concat("date",' ',"time")::timestamp),
					floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
					min("time") "time","date",
					max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
				sum(labour_time) labour_time
					from (
							SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
						sum(case when object_name = 'labour' then 10 end) labour_time,
							object_name, channel, 
							max("date")::varchar "date",cast(time as varchar) time, 
						case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
							max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
							concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
							sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
							max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
							FROM public.app_lt_july_01_final_data_12_hours
							where duplicate is null and (object_name = 'labour' or class_id is null)
							and confidence_score >= 0.6
							group by object_name, channel, 
							date, "time", file_name, activity, milestone
						)a
					group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
					floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
				) a
			group by left(time::varchar,5),labour_count,no_helmet,file_name
			)  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
			group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
			b.idle,b.group_event,a.date,b.no_helmet,file_name
			order by a."date",1
"""


from django.http import JsonResponse
from django.db import connection
from django.views import View
from django.http import JsonResponse
from django.db import connection
from django.views import View

class Workforce_IdleDataView(View):
    def get(self, request):
        with connection.cursor() as cursor:
            print("Executing Base Query")
            cursor.execute(query_workforce_idle_date)  # ✅ Always run the base query

            # ✅ Check if any columns are returned before fetching data
            if cursor.description is None:
                print("No columns returned by the query!")
                return JsonResponse({"error": "No data available"}, status=404)

            result = cursor.fetchall()

        # ✅ Ensure we have results before processing
        if not result:
            print("Query executed but returned no rows!")
            return JsonResponse({"error": "No data available"}, status=404)

        print(f"Fetched {len(result)} rows")

        data = {}
        for row in result:
            print(row)  # Debugging: Print each row
            time_key = row[0]
            labour_count = row[1]
            idle_status = row[2]
            group_event = row[3]
            date_str = row[4]
            no_helmet = row[5]
            image_filename = row[6]

            image_url = f"/media/{image_filename}" if image_filename else None

            data[time_key] = [
                labour_count, idle_status, group_event, date_str, no_helmet, image_url
            ]

        return JsonResponse(data, safe=False)


class WorkforceIdleDataWithoutDateView(View):
    def get(self, request):
        query = """ 
       WITH dates AS (
    SELECT 
        date(DATE '2024-07-01' + INTERVAL '1 day' * (n - 1)) AS date
    FROM 
        generate_series(1, 1) AS n
),
numbers AS (
    SELECT time_g,left(right(time_g::varchar,8),5) time_g_t
FROM generate_series
        ( '2024-07-01'::timestamp 
        , '2024-07-02'::timestamp
        , '5 minutes'::interval) time_g
	where date(time_g) <> '2024-07-02'
)
select a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end labour_count,
b.idle,b.group_event,a.date::text,b.no_helmet,file_name img,sum(labour_time) labour_time from 
(SELECT 
    d.date::date date,
    n.time_g time,time_g_t--,FLOOR(RANDOM() * 2600) r_value
FROM 
    dates d
CROSS JOIN 
    numbers n ) a
left join (
	Select left(time::varchar,5) time,case when labour_count is null then 0 else labour_count end labour_count,
max(idle) idle,max(group_event) group_event,max("date"::varchar) "date",no_helmet,file_name,sum(labour_time) labour_time from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,max(file_name) file_name,
	sum(labour_time) labour_time
		from (
				SELECT activity, milestone,sum(case when object_name = 'labour' then 1 end) labour_count,
			sum(case when object_name = 'labour' then 10 end) labour_time,
				object_name, channel, 
				max("date")::varchar "date",cast(time as varchar) time, 
			case when max(idle) = 'true' or max(group_event) = 'true' then file_name end file_name,
				max(group_event) group_event,max(idle) idle,max(no_helmet)  no_helmet,
				concat(cast(date as varchar),' ',cast(time as varchar)) date_time,sum(group_count) group_count,
				sum(idle_count) idle_count,max(no_helmet_count) no_helmet_count,max(no_vest) no_vest,
				max(no_vest_count) no_vest_count,array_agg(box_coordinates) box_coordinates
				FROM public.app_lt_july_01_final_data_12_hours
				where duplicate is null and (object_name = 'labour' or class_id is null)
			and confidence_score >= 0.6
				group by object_name, channel, 
				date, "time", file_name, activity, milestone
			 )a
		group by date_part('hour', concat("date",' ',"time")::timestamp),"date",
		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
	) a
group by left(time::varchar,5),labour_count,no_helmet,file_name
)  b on a."date"::varchar = b."date"::varchar and a.time_g_t = b."time"
group by a.time_g_t,case when b.labour_count is null then 0 else b.labour_count end,
b.idle,b.group_event,a.date,b.no_helmet,file_name

order by a."date",1
        """
        
        try:
            data = execute_raw_query(query)

            if not data:
                return JsonResponse({"error": "No data available"}, status=404)

            return JsonResponse(data, safe=False)

        except Exception as e:
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

import json
from django.http import JsonResponse
from django.db import connection
from django.views import View

class PieChartDataView(View):
    def get(self, request):
        query = """
      Select 'Active' Name,concat(round(((sum(labour_time_seconds) - (sum(timeidle_seconds) + sum(timegrp_seconds)))/sum(labour_time_seconds))*100,2),' %')  "value"
 from (
Select left(time::varchar,5),case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,timegrp timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,timeidle timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 labour_time labour_time_seconds,
  TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 310 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 310 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date" = c."date" and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,5),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a

union all

Select 'Idle' Name,concat(round((sum(timeidle_seconds)/sum(labour_time_seconds))*100,2),' %') "value"
 from (
Select left(time::varchar,5),case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,timegrp timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,timeidle timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 labour_time labour_time_seconds,
  TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 310 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 310 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date" = c."date" and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,5),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a

union all

Select 'Group' Name,concat(round((sum(timegrp_seconds)/sum(labour_time_seconds))*100,2),' %') "value"
 from (
Select left(time::varchar,5),case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,timegrp timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,timeidle timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 labour_time labour_time_seconds,
  TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 310 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 310 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date" = c."date" and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,5),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return JsonResponse(result, safe=False)
    
from django.shortcuts import render

def caging_view(request):
    return render(request, "caging.html")


from django.urls import reverse

def get_pier_progress_data(request):
    data = [
        {"title": "Rebaring", "measures": [40, 50], "url": "/rebaring.html"},
        {"title": "Caging", "measures": [30, 70], "url": reverse('caging')},  # Django URL
        {"title": "Molding", "measures": [60, 70], "url": "/molding.html"},
    ]
    return JsonResponse({"progress_data": data})

import json
from collections import defaultdict
from django.http import JsonResponse
from django.db import connections

# Define the SQL query
query_pier_progress = """
SELECT activity, milestone, ROUND(AVG(labour_count))::int AS labour_count,
SUM(working_hours) AS working_hours, SUM(active_hours) AS active_hours,
SUM(inactive_hours) AS inactive_hours, SUM(total_planned_hrs) AS total_planned_hrs, COUNT(date) AS day_count,
CASE WHEN COUNT(date) > 3 THEN 'Delay' ELSE 'On Time' END AS delay_status
FROM excel
GROUP BY activity, milestone
ORDER BY 2
"""

def get_data_pier_progress(request):
    """
    Django view to fetch Pier Progress data and return it as JSON.
    """
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(query_pier_progress)
            result = cursor.fetchall()

        print("Query Result:", result)  # Debugging (Remove in production)

        # Convert query result into structured JSON
        data = defaultdict(list)
        for row in result:
            value = {
                'milestone': row[1],
                'labour_count': row[2],
                'working_hours': row[3],
                'active_hours': row[4],
                'inactive_hours': row[5],
                'total_planned_hrs': row[6],  # Fixed index
                'day_count': row[7],          # Fixed index
                'delay_status': row[8],       # Fixed index
            }
            data[row[0]].append(value)

        return JsonResponse(data, safe=False)

    except Exception as e:
        print("Database error:", str(e))
        return JsonResponse({'error': 'Database query failed'}, status=500)



import json
from django.http import JsonResponse
from django.db import connections

# Define SQL Queries
query_group_talk = """
SELECT activity, milestone, count(class_id) object_count, object_name, channel, 
cast(date as varchar) date, cast(time as varchar) time, file_name,
processing_time, max(group_talking) group_talking, max(idle) idle, max(no_helmet) no_helmet,
concat(cast(date as varchar), ' ', cast(time as varchar)) date_time, count(1) total_count
FROM public.app_office_data_4_7_co_ord
GROUP BY object_name, channel, date, "time", file_name, processing_time, activity, milestone
HAVING max(group_talking) ILIKE %(group_talking)s
ORDER BY date, "time" DESC, file_name
"""

query_idle = """
SELECT activity, milestone, count(class_id) object_count, object_name, channel, 
cast(date as varchar) date, cast(time as varchar) time, file_name,
processing_time, max(group_talking) group_talking, max(idle) idle, max(no_helmet) no_helmet,
concat(cast(date as varchar), ' ', cast(time as varchar)) date_time, count(1) total_count
FROM public.app_office_data_4_7_co_ord
GROUP BY object_name, channel, date, "time", file_name, processing_time, activity, milestone
HAVING max(idle) ILIKE %(idle)s
ORDER BY date, "time" DESC, file_name
"""

query_no_helmet = """
SELECT activity, milestone, count(class_id) object_count, object_name, channel, 
cast(date as varchar) date, cast(time as varchar) time, file_name,
processing_time, max(group_talking) group_talking, max(idle) idle, max(no_helmet) no_helmet,
concat(cast(date as varchar), ' ', cast(time as varchar)) date_time, count(1) total_count
FROM public.app_office_data_4_7_co_ord
GROUP BY object_name, channel, date, "time", file_name, processing_time, activity, milestone
HAVING max(no_helmet) ILIKE %(no_helmet)s
ORDER BY date, "time" DESC, file_name
"""

query_all = """
SELECT activity, milestone, count(CASE WHEN object_name = 'labour' THEN 1 END) labour_count,
object_name, channel, cast(date as varchar) date, cast(time as varchar) time, file_name,
processing_time, max(group_talking) group_talking, max(idle) idle, max(no_helmet) no_helmet,
concat(cast(date as varchar), ' ', cast(time as varchar)) date_time, sum(group_count) group_count,
sum(idle_count) idle_count, max(no_helmet_count) no_helmet_count, max(no_vest) no_vest,
max(no_vest_count) no_vest_count, array_agg(box_coordinates) box_coordinates
FROM public.app_lt_july_01_final_data
WHERE duplicate IS NULL 
AND (object_name = 'labour' OR class_id IS NULL)
AND cast(extract(minute from time) as integer) % 3 = '0'
AND cast(extract(second from time) as integer) = '00'
GROUP BY object_name, channel, date, "time", file_name, processing_time, activity, milestone
ORDER BY date, "time", file_name
"""

def get_data(request):
    """
    Django view to fetch data based on filters (group_talking, idle, no_helmet).
    """
    group_talking = request.GET.get('group_talking', '')
    idle = request.GET.get('idle', '')
    no_helmet = request.GET.get('no_helmet', '')

    try:
        with connections['default'].cursor() as cursor:
            if group_talking:
                cursor.execute(query_group_talk, {'group_talking': f"{group_talking}%"})
            elif idle:
                cursor.execute(query_idle, {'idle': f"%{idle}%"})
            elif no_helmet:
                cursor.execute(query_no_helmet, {'no_helmet': f"%{no_helmet}%"})
            else:
                cursor.execute(query_all)

            result = cursor.fetchall()

        # Convert query result into structured JSON
        data = [
            {
                'activity': row[0],
                'milestone': row[1],
                'labour_count': row[2],
                'channel': row[4],
                'date': row[5],
                'time': row[6],
                'file_name': row[7],
                'group_talking': row[9],
                'idle': row[10],
                'no_helmet': row[11],
                'date_time': row[12],
                'no_vest': row[16],
                'box_coordinates': row[18]
            }
            for row in result
        ]

        return JsonResponse(data, safe=False)

    except Exception as e:
        print("Database error:", str(e))
        return JsonResponse({'error': 'Database query failed'}, status=500)


import json
from django.http import JsonResponse
from django.db import connections

# Define the SQL query
query_pie_chart = """
Select 'Active' Name,concat(round(((sum(labour_time_seconds) - (sum(timeidle_seconds) + sum(timegrp_seconds)))/sum(labour_time_seconds))*100,2),' %')  "value"
 from (
Select left(time::varchar,5),case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,timegrp timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,timeidle timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 labour_time labour_time_seconds,
  TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 310 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 310 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date" = c."date" and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,5),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a

union all

Select 'Idle' Name,concat(round((sum(timeidle_seconds)/sum(labour_time_seconds))*100,2),' %') "value"
 from (
Select left(time::varchar,5),case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,timegrp timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,timeidle timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 labour_time labour_time_seconds,
  TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 310 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 310 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date" = c."date" and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,5),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a

union all

Select 'Group' Name,concat(round((sum(timegrp_seconds)/sum(labour_time_seconds))*100,2),' %') "value"
 from (
Select left(time::varchar,5),case when labour_count is null then 0 else labour_count end labour_count,
idle,group_event,max("date"::varchar) "date",no_helmet ,
case when group_count is null then 0 else group_count end group_count,timegrp timegrp_seconds,
 TO_CHAR(((case when timegrp is null then 0 else timegrp end) || ' second')::interval, 'HH24:MI:SS')  timegrp,
case when idle_count is null then 0 else idle_count end idle_count,timeidle timeidle_seconds,
 TO_CHAR(((case when timeidle is null then 0 else timeidle end) || ' second')::interval, 'HH24:MI:SS')  timeidle,
 labour_time labour_time_seconds,
  TO_CHAR(((case when labour_time is null then 0 else labour_time end) || ' second')::interval, 'HH24:MI:SS')  labour_time
from (
		select date_part('hour', concat("date",' ',"time")::timestamp),
-- 		floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5 grp_time,
		min("time") "time","date",
		max(labour_count) labour_count,max(no_helmet) no_helmet,max(idle) idle,max(group_event) group_event,
		max(group_count) group_count,sum(timegrp) timegrp,max(idle_count) idle_count,sum(timeidle) timeidle,sum(labour_time) labour_time
		from (
			SELECT a.activity, a.milestone,sum(case when a.object_name = 'labour' then 1 end) labour_count,
			a.object_name, a.channel, 
			max(a."date")::varchar "date",cast(a.time as varchar) time, a.file_name,
			max(a.group_event) group_event,max(a.idle) idle,max(a.no_helmet)  no_helmet,
			concat(cast(a.date as varchar),' ',cast(a.time as varchar)) date_time,sum(a.group_count) group_count,
			sum(a.idle_count) idle_count,max(a.no_helmet_count) no_helmet_count,max(a.no_vest) no_vest,
			max(a.no_vest_count) no_vest_count,array_agg(a.box_coordinates) box_coordinates,
			a.gps,sum(timegrp) timegrp,a.ids,sum(timeidle) timeidle,sum(labour_time) labour_time
			FROM (
	-------------------------				
				select case when group_event = 'true' and group_talking = 'true' and gps = 'Group Start' then 310 
				when group_event = 'true' and group_talking = 'true' and gps is null then 10 end timegrp,
				case when ids = 'Idle Start' then 310 
				when ids = 'idlemem' then 10 end timeidle,case when class_id = 0 then 10 end labour_time,
				a.*,b.gps,c.ids from public.app_lt_july_01_final_data_12_hours a
				left join 
					(Select "date","time",gps from (
						select case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
						lag(time_stamp) over ( order by "time" ) is null  then 'Group Start' else 'groupmem' end gps,
						lag(time_stamp) over (order by "time" ),time_stamp,
						lag("time") over (order by "time" ),"time",
						case when lag("time") over ( order by "time" ) is null or 
						lag("time") over (order by "time" ) + interval '10 seconds' <> "time" then 'Group Start' end grp_st_ind,
						id,track_id,eucl,file_name,"date",x1,y1,cx,cy,group_event,group_talking 
						from  public.app_lt_july_01_final_data_12_hours
						where group_event = 'true' ) a
					where gps = 'Group Start'
					) b on a."date" = b."date" and a."time" = b."time" and a.class_id = 0
				left join (
				Select "date","time",ids from (
					select 
					case when time_stamp - lag(time_stamp) over (order by "time" ) > 10 or 
					lag(time_stamp) over ( order by "time" ) is null  then 'Idle Start' else 'idlemem' end ids,
					lag(time_stamp) over (order by "time" ),time_stamp,
					lag("time") over (order by "time" ),
					id,track_id,eucl,file_name,"date","time",x1,y1,cx,cy,group_event,group_talking 
					from  public.app_lt_july_01_final_data_12_hours
					where idle = 'true' ) a
				) c on a."date" = c."date" and a."time" = c."time" and a.class_id = 0 and a.idle = 'true'
				) a
				where duplicate is null and (object_name = 'labour' or class_id is null)
				group by object_name, channel, 
				a.date, a."time", a.file_name, a.activity, a.milestone,a.gps,a.ids
					)a
			group by date_part('hour', concat("date",' ',"time")::timestamp),"date"
-- 			floor(date_part('minutes', concat("date",' ',"time")::timestamp)/5)*5
		) a
group by left(time::varchar,5),labour_count,idle,group_event,no_helmet,group_count,timegrp,idle_count,timeidle,labour_time
) a
"""

def get_data_pie(request):
    """
    Django API to fetch Pie Chart data and return JSON.
    """
    try:
        with connections['default'].cursor() as cursor:
            cursor.execute(query_pie_chart)
            result = cursor.fetchall()

        # Convert query result into a dictionary
        data = {}
        for row in result:
            name = row[0]
            value = row[1]
            data[name] = value

        return JsonResponse(data, safe=False)

    except Exception as e:
        print("Database error:", str(e))
        return JsonResponse({'error': 'Database query failed'}, status=500)



class WorkforceActivityView(View):
    def get(self, request):
        data = list(get_workforce_activity())
        return JsonResponse({'data': data}, safe=False)

class WorkforceIdleView(View):
    def get(self, request):
        data = list(get_workforce_idle())
        return JsonResponse({'data': data}, safe=False)

class GroupTalkingView(View):
    def get(self, request):
        data = list(get_group_talking_events())
        return JsonResponse({'data': data}, safe=False)

class PieChartView(View):
    def get(self, request):
        data = get_pie_chart_data()
        return JsonResponse({'data': data}, safe=False)

class PierProgressView(View):
    def get(self, request):
        data = list(get_pier_progress())
        return JsonResponse({'data': data}, safe=False)
