import random
from copy import deepcopy


def make_hour(hour, *, bad=False):
    if bad:
        return {
            "hour": hour,
            "latency_ms": random.randint(170, 320),
            "packet_loss_pct": round(random.uniform(7.5, 15.5), 1),
            "disconnects": random.randint(2, 7),
            "connected_devices": random.randint(95, 180),
            "signal_dbm": random.randint(-78, -62),
            "is_bad": True,
        }

    return {
        "hour": hour,
        "latency_ms": random.randint(18, 90),
        "packet_loss_pct": round(random.uniform(0.2, 2.1), 1),
        "disconnects": random.randint(0, 1),
        "connected_devices": random.randint(26, 90),
        "signal_dbm": random.randint(-68, -45),
        "is_bad": False,
    }


def build_hourly_metrics(bad_hours=None):
    bad_hours = set(bad_hours or [])
    return [make_hour(hour, bad=hour in bad_hours) for hour in range(24)]


ROUTERS = [
    {
        "router_id": "R-1042",
        "building": "North Hall",
        "room": "N-204",
        "model": "Cisco 9120",
        "firmware_version": "1.4.2",
        "user_type": "student",
        "health_score": 28,
        "bad_hours_count": 14,
        "complaints": [
            {"ticket_id": "TCK-2217", "date": "2026-08-06", "complaint_text": "Frequent disconnects during lecture hours and slow Wi-Fi in the west wing."},
            {"ticket_id": "TCK-2241", "date": "2026-08-07", "complaint_text": "Students report the AP drops connection every 15 minutes between 2pm and 7pm."},
        ],
        "breakdown": {
            "latency": "critical",
            "packet_loss": "critical",
            "signal": "warning",
            "disconnects": "critical",
        },
        "metrics_timeseries": build_hourly_metrics(set(range(5, 19))),
    },
    {
        "router_id": "R-1025",
        "building": "Engineering Block",
        "room": "E-118",
        "model": "Aruba 535",
        "firmware_version": "2.0.1",
        "user_type": "staff",
        "health_score": 83,
        "bad_hours_count": 1,
        "complaints": [
            {"ticket_id": "TCK-2278", "date": "2026-08-04", "complaint_text": "A single short outage this afternoon; usually stable."},
        ],
        "breakdown": {
            "latency": "healthy",
            "packet_loss": "healthy",
            "signal": "healthy",
            "disconnects": "warning",
        },
        "metrics_timeseries": build_hourly_metrics({10}),
    },
    {
        "router_id": "R-2010",
        "building": "Library Annex",
        "room": "L-402",
        "model": "Juniper EX2300",
        "firmware_version": "3.1.9",
        "user_type": "faculty",
        "health_score": 91,
        "bad_hours_count": 0,
        "complaints": [],
        "breakdown": {
            "latency": "healthy",
            "packet_loss": "healthy",
            "signal": "healthy",
            "disconnects": "healthy",
        },
        "metrics_timeseries": build_hourly_metrics(),
    },
    {
        "router_id": "R-3015",
        "building": "South Residence",
        "room": "SR-215",
        "model": "Ubiquiti U6-Pro",
        "firmware_version": "4.2.3",
        "user_type": "student",
        "health_score": 76,
        "bad_hours_count": 2,
        "complaints": [
            {"ticket_id": "TCK-2308", "date": "2026-08-05", "complaint_text": "Students mention weak signal near the stairwell at night."},
        ],
        "breakdown": {
            "latency": "healthy",
            "packet_loss": "healthy",
            "signal": "warning",
            "disconnects": "healthy",
        },
        "metrics_timeseries": build_hourly_metrics({21, 22}),
    },
    {
        "router_id": "R-1104",
        "building": "North Hall",
        "room": "N-108",
        "model": "Cisco 9120",
        "firmware_version": "1.3.8",
        "user_type": "student",
        "health_score": 44,
        "bad_hours_count": 8,
        "complaints": [
            {"ticket_id": "TCK-2016", "date": "2026-08-03", "complaint_text": "Slow connections during evening study sessions."},
        ],
        "breakdown": {
            "latency": "warning",
            "packet_loss": "warning",
            "signal": "warning",
            "disconnects": "healthy",
        },
        "metrics_timeseries": build_hourly_metrics(set(range(17, 23))),
    },
    {
        "router_id": "R-2201",
        "building": "Business School",
        "room": "BS-205",
        "model": "Meraki MR46",
        "firmware_version": "2.5.8",
        "user_type": "faculty",
        "health_score": 66,
        "bad_hours_count": 4,
        "complaints": [],
        "breakdown": {
            "latency": "warning",
            "packet_loss": "healthy",
            "signal": "healthy",
            "disconnects": "healthy",
        },
        "metrics_timeseries": build_hourly_metrics({14, 15, 16, 17}),
    },
    {
        "router_id": "R-3308",
        "building": "Admin Block",
        "room": "A-410",
        "model": "Aruba 515",
        "firmware_version": "2.8.7",
        "user_type": "staff",
        "health_score": 52,
        "bad_hours_count": 9,
        "complaints": [
            {"ticket_id": "TCK-2450", "date": "2026-08-06", "complaint_text": "Office traffic is slow and reconnects repeatedly during lunch hour."},
        ],
        "breakdown": {
            "latency": "warning",
            "packet_loss": "warning",
            "signal": "healthy",
            "disconnects": "warning",
        },
        "metrics_timeseries": build_hourly_metrics(set(range(12, 20))),
    },
    {
        "router_id": "R-4407",
        "building": "Research Wing",
        "room": "RW-102",
        "model": "Huawei AirEngine",
        "firmware_version": "5.0.2",
        "user_type": "researcher",
        "health_score": 88,
        "bad_hours_count": 0,
        "complaints": [],
        "breakdown": {
            "latency": "healthy",
            "packet_loss": "healthy",
            "signal": "healthy",
            "disconnects": "healthy",
        },
        "metrics_timeseries": build_hourly_metrics(),
    },
    {
        "router_id": "R-5503",
        "building": "South Residence",
        "room": "SR-305",
        "model": "Cisco 9120",
        "firmware_version": "1.5.4",
        "user_type": "student",
        "health_score": 73,
        "bad_hours_count": 3,
        "complaints": [
            {"ticket_id": "TCK-2521", "date": "2026-08-07", "complaint_text": "Service is fine most of the day, but a few evening hours are laggy."},
        ],
        "breakdown": {
            "latency": "healthy",
            "packet_loss": "healthy",
            "signal": "warning",
            "disconnects": "healthy",
        },
        "metrics_timeseries": build_hourly_metrics({18, 19, 20}),
    },
    {
        "router_id": "R-6602",
        "building": "Engineering Block",
        "room": "E-221",
        "model": "Ubiquiti U6-LR",
        "firmware_version": "4.9.4",
        "user_type": "staff",
        "health_score": 35,
        "bad_hours_count": 12,
        "complaints": [
            {"ticket_id": "TCK-2387", "date": "2026-08-05", "complaint_text": "Signal degradation is visible around the lab benches during custom experiments."},
        ],
        "breakdown": {
            "latency": "critical",
            "packet_loss": "warning",
            "signal": "warning",
            "disconnects": "warning",
        },
        "metrics_timeseries": build_hourly_metrics(set(range(8, 19))),
    },
]


def get_all_rankings():
    rankings = []
    for item in deepcopy(ROUTERS):
        rankings.append(
            {
                "router_id": item["router_id"],
                "health_score": item["health_score"],
                "building": item["building"],
                "bad_hours_count": item["bad_hours_count"],
                "firmware_version": item["firmware_version"],
            }
        )
    return sorted(rankings, key=lambda router: router["health_score"])


def get_router_detail(router_id):
    for item in ROUTERS:
        if item["router_id"] == router_id:
            return {
                "router_id": item["router_id"],
                "info": {
                    "building": item["building"],
                    "room": item["room"],
                    "model": item["model"],
                    "firmware_version": item["firmware_version"],
                    "user_type": item["user_type"],
                },
                "health_score": item["health_score"],
                "breakdown": item["breakdown"],
                "metrics_timeseries": item["metrics_timeseries"],
                "complaints": item["complaints"],
            }
    return None


def get_router_by_id(router_id):
    for item in ROUTERS:
        if item["router_id"] == router_id:
            return item
    return None
