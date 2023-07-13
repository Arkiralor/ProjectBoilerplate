from redis import Redis
import datetime

job = {
    "connection": "Redis<ConnectionPool<Connection<host=127.0.0.1,port=6379,db=0>>>",
    "_id": "fe4b6c94-1814-41db-ba59-b9ddeedad520",
    "created_at": datetime.datetime(2023, 7, 12, 23, 42, 45, 25246),
    "_data": "b""\\x80\\x05\\x95V\\x00\\x00\\x00\\x00\\x00\\x00\\x00(\\x8c(job_handler_app.utils.find_prime_numbers\\x94N)}\\x94(\\x8c\\x0blower_bound\\x94K\\x19\\x8c\\x0bupper_bound\\x94M9\\x03ut\\x94.",
    "_func_name": "job_handler_app.utils.find_prime_numbers",
    "_instance": None,
    "_args": "()",
    "_kwargs": {
        "lower_bound": 25,
        "upper_bound": 825
    },
    "_success_callback_name": None,
    "_success_callback": "< object object at 0x7fbccdaf8c60 >",
    "_failure_callback_name": None,
    "_failure_callback": "< object object at 0x7fbccdaf8c60 >",
    "_stopped_callback_name": None,
    "_stopped_callback": "< object object at 0x7fbccdaf8c60 >",
    "description": "job_handler_app.utils.find_prime_numbers(lower_bound=25, upper_bound=825)",
    "origin": "default",
    "enqueued_at": datetime.datetime(2023, 7, 12, 23, 42, 45, 26173),
    "started_at": None,
    "ended_at": None,
    "_result": None,
    "_exc_info": None,
    "timeout": 180,
    "_success_callback_timeout": None,
    "_failure_callback_timeout": None,
    "_stopped_callback_timeout": None,
    "result_ttl": None,
    "failure_ttl": None,
    "ttl": None,
    "worker_name": None,
    "_status": "<JobStatus.QUEUED\": \"queued\"\">",
    "_dependency_ids": [

    ],
    "meta": {

    },
    "serializer": "<class""rq.serializers.DefaultSerializer"">",
    "retries_left": None,
    "retry_intervals": None,
    "redis_server_version": (7, 0, 12),
    "last_heartbeat": None,
    "allow_dependency_failures": None,
    "enqueue_at_front": None,
    "_cached_result": None
}

failed_job = {
    "connection": "Redis < ConnectionPool < Connection < host = 127.0.0.1,port = 6379,db = 0 >> >",
    "_id": "2d6db9b6-d89c-412f-b83a-da89d76c911b",
    "created_at": datetime.datetime(2023, 7, 12, 23, 49, 7, 901960),
    "_data": "b""\\x80\\x05\\x95X\\x00\\x00\\x00\\x00\\x00\\x00\\x00(\\x8c(job_handler_app.utils.find_prime_numbers\\x94N)}\\x94(\\x8c\\x0blower_bound\\x94K\n\\x8c\\x0bupper_bound\\x94J@B\\x0f\\x00ut\\x94.",
    "_func_name": "< object object at 0x7f078c0d1c60 >",
    "_instance": "< object object at 0x7f078c0d1c60 >",
    "_args": "< object object at 0x7f078c0d1c60 >",
    "_kwargs": "< object object at 0x7f078c0d1c60 >",
    "_success_callback_name": None,
    "_success_callback": "< object object at 0x7f078c0d1c60 >",
    "_failure_callback_name": None,
    "_failure_callback": "< object object at 0x7f078c0d1c60 >",
    "_stopped_callback_name": None,
    "_stopped_callback": "< object object at 0x7f078c0d1c60 >",
    "description": "job_handler_app.utils.find_prime_numbers(lower_bound=10, upper_bound=1000000)",
    "origin": "default",
    "enqueued_at": datetime.datetime(2023, 7, 12, 23, 49, 7, 903165),
    "started_at": datetime.datetime(2023, 7, 12, 23, 49, 7, 910282),
    "ended_at": datetime.datetime(2023, 7, 12, 23, 52, 7, 910652),
    "_result": None,
    "_exc_info": None,
    "timeout": 180,
    "_success_callback_timeout": None,
    "_failure_callback_timeout": None,
    "_stopped_callback_timeout": None,
    "result_ttl": None,
    "failure_ttl": None,
    "ttl": None,
    "worker_name": "cf666cd0f46d416d9bbe4b8ce31954d6",
    "_status": "failed",
    "_dependency_ids": [

    ],
    "meta": {

    },
    "serializer": "<class\"\"rq.serializers.DefaultSerializer\"\">",
    "retries_left": None,
    "retry_intervals": None,
    "redis_server_version": None,
    "last_heartbeat": datetime.datetime(2023, 7, 12, 23, 52, 7, 911730),
    "allow_dependency_failures": None,
    "enqueue_at_front": None,
    "_cached_result": None
}
