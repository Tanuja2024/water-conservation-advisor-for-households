from firebase_admin import db
import datetime
from collections import defaultdict

def compute_total_usage(grouped_data):
    labels = []
    totals = []
    for time_unit, usage in grouped_data.items():
        labels.append(time_unit)
        totals.append(sum(usage.values()))
    return labels, totals

def prepare_grouped_data_for_chart(grouped_data):
    resource_set = set()
    for usage in grouped_data.values():
        resource_set.update(usage.keys())
    resource_list = list(resource_set)

    labels = sorted(grouped_data.keys())  # e.g., "01", "02", ..., "12"
    data_by_resource = {res: [] for res in resource_list}

    for month in labels:
        usage = grouped_data.get(month, {})
        for res in resource_list:
            data_by_resource[res].append(usage.get(res, 0))

    return labels, data_by_resource

def get_year_data(client_id, year):
    ref = db.reference(f"/Clients/{client_id}/daily_usage/{year}")
    return ref.get()  # returns a dict {month: {day: {usage}}}


def aggregate_monthly_usage(year_data):
    from collections import defaultdict

    # Pre-fill months with empty usage
    monthly_totals = {f"{i:02d}": defaultdict(int) for i in range(1, 13)}

    for month, days in year_data.items():
        for day, usage in days.items():
            for resource, gallons in usage.items():
                monthly_totals[month][resource] += gallons

    # Convert inner defaultdicts to normal dicts
    return {month: dict(usage) for month, usage in monthly_totals.items()}


def get_week_number(year, month, day):
    date_obj = datetime.datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
    return date_obj.isocalendar()[1]  # ISO week number

def aggregate_weekly_usage(month_data, year, month):
    weekly_totals = {f"Week {i}": defaultdict(int) for i in range(1, 5)}  # Week 1–4

    sorted_days = sorted(month_data.keys(), key=lambda d: int(d))
    for day in sorted_days:
        day_int = int(day)
        week_number = (day_int - 1) // 7 + 1  # 1-based
        week_label = f"Week {week_number}"

        for resource, gallons in month_data[day].items():
            weekly_totals[week_label][resource] += gallons

    return {week: dict(usage) for week, usage in weekly_totals.items()}

