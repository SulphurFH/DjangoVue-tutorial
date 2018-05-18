import redis

code_pool = redis.ConnectionPool(host='192.168.0.88', port=6379, db=2)
times_pool = redis.ConnectionPool(host='192.168.0.88', port=6379, db=3)


class RedisClient():
    mobile_verify_code_db = redis.StrictRedis(connection_pool=code_pool)
    mobile_verify_times_db = redis.StrictRedis(connection_pool=times_pool)


MobileVerifyKind = {
    "REGISTER": 1
}
