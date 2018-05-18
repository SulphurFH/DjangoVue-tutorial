import random
import time
from rest_framework import status

from config.redis_conf import RedisClient, MobileVerifyKind
from .models import VerifyCode


class MobileVerifyLimit():
    """
    用于限制手机验证次数

    实现方式:

        在Redis中使用List进行时间戳的记录
        限制条件为连续性限制,并非周期性,如下所示

           1:00       1:20       1:40       2:00       2:20
         ---|----------|----------|----------|----------|---
            √          √          √

        例如在一小时内限制发送3次,上面时间轴中,√ 表示发送一次,则在2:00前,是不可以再发送的,因为已经发送了三次

           1:00       1:20       1:40       2:00       2:20
         ---|----------|----------|----------|----------|---
            √          √          √
            |-|--------|----------|----------|-|
             1:01                             2:01

        若当前时间为2:01,则一小时内(从1:01 ~ 2:01)只发送了两条,因为1:00发送的那条,时间已经不在当前时间的一小时内,所以可以再发送一条.


           1:00       1:20       1:40       2:00       2:20
         ---|----------|----------|----------|----------|---
           √*          √          √            √

        以此类推,当时间到了2:20后,可以再次发送一条,每次计算周期,均以当前时间往前推一个周期,然后统计次数

    PS: 为展现方便,时间戳用简短数字表示

    限制条件: 6秒内只允许发送3次

    EXP 1:  List 中已经有数据

        1) 可以继续插入的情况: List >> HEAD: [6, 3, 1] :END Expire at 12, 队列中最大值`6`+周期`6` = 12

        此时时间戳为 8,因为限制次数是3,则取出距离HEAD的第三个元素`1`,然后判断当前时间戳与这个时间戳的差值 8 - 1 = 7,差值 > 周期`6`,
        说明周期内触发的时间戳没有达到上限,此时可以继续插入
        并且此时队列中数据已经达到队列上限,即次数的上限,此时在第二次运营rpop命令,将已经过期的数据pop出去

        2) 不可以继续插入的情况: List >> HEAD: [6, 5, 4] :END Expire at 12, 队列中最大值`6`+周期`6` = 12

        此时时间戳为 7,因为限制次数是3,则取出距离HEAD的第三个元素`4`,然后判断当前时间戳与这个时间戳的差值 7 - 4 = 3,差值 < 周期`6`,
        说明周期内触发的时间戳已经达到上限,此时不可以插入

    EXP 2: List 中没有数据

        此种情况较为简单,因队列是空的,所以说明里面一条记录都没有,直接推进新的数据即可

    使用的redis命令:
    lpush O(1)
    rpop O(1)
    lindex O(n) - 当操作队列或队尾的时候,相当于 O(1),实际测试中发现并非与理想效果一致

    优化了队列长度的限制,及清理方式,如果lindex操作的队尾确实是O(1)复杂度,则在限制队列长度的情况下,redis操作全部为O(1)
    对于redis cpu密集型处理,时间复杂度的优化会大幅优化redis的性能.
    """
    client = RedisClient.mobile_verify_times_db
    cache_key = 'MB:VF:LT:{kind}:{prefix}:{period}'

    VAL = 'val'
    TIMES = 'times'
    UNIT = 'unit'

    S = 1
    M = 60
    H = 60 * M
    D = 24 * H

    LIMIT_SETTINGS = {
        MobileVerifyKind['REGISTER']: [
            {VAL: 1, TIMES: 1, UNIT: M},
            {VAL: 1, TIMES: 1, UNIT: M}
        ],
    }

    DEFAULT_LIMIT = [
        {VAL: 1, TIMES: 1, UNIT: M},
        {VAL: 1, TIMES: 1, UNIT: M}
    ]

    @classmethod
    def format_key(cls, kind, prefix, period):
        return cls.cache_key.format(kind=kind, prefix=prefix, period=period)

    @classmethod
    def get_limit_conf(cls, kind):
        """
        获取配置信息，后期还可以扩展
        """
        return cls.LIMIT_SETTINGS.get(kind) or cls.DEFAULT_LIMIT

    @classmethod
    def process_exec(cls, exec_list):
        """
        处理redis命令列表
        :param exec_list: redis命令列表 ('action', 'key', 'args')
        :return: pipline执行结果
        """
        now_ts = int(time.time())
        pipeline = cls.client.pipeline()
        for item in exec_list:
            if item[0] == 'lpush':
                pipeline.lpush(item[1], now_ts)
                pipeline.expire(item[1], item[2])
            elif item[0] == 'rpop':
                pipeline.rpop(item[1])
        return pipeline.execute()

    @classmethod
    def rollback_exec(cls, exec_list):
        """
        通过redis命令列表,将上次操作回滚
        :param exec_list: redis命令列表 ('action', 'key', 'args')
        :return: pipline执行结果
        """
        pipeline = cls.client.pipeline()
        for item in exec_list:
            if item[0] == 'rpop':
                pipeline.rpop(item[1])
        return pipeline.execute()

    @classmethod
    def is_limited(cls, prefix, kind):
        """
        判断是否限制住了次数,prefix为限制的参数,如果要限制一个手机,则传递手机号,如果限制用户,则传递用户ID
        :param prefix: 限制参数
        :param kind: 种类
        :return: 是否限制了,如果返回`True`,则说明限制住了,`False`则说明没有限制,可以发送
        """
        # 取出限制配置
        conf = cls.get_limit_conf(kind)
        # 如果存在配置,则开始验证,否则返回`False`,说明没有限制
        if conf:
            exec_list = []
            pipeline = cls.client.pipeline()
            # 遍历配置中的限制条件
            for item in conf:
                # 先计算下周期,默认使用`秒`作为单位
                period = item[cls.VAL] * (item.get(cls.UNIT) or cls.S)
                # 格式化key
                key = cls.format_key(kind, prefix, period)
                # 取出限制的次数
                conf_times = item[cls.TIMES]
                # 增加命令,取出限制次数的index值
                pipeline.lindex(key, conf_times - 1)
                # 向命令记录列表中添加记录,用于第二次处理
                exec_list.append((key, period))
            # 初始化第二次执行的命令列表
            sec_exec_list = []
            # 生成当前时间戳
            now_ts = time.time()
            # 开始便利第一次执行的结果,并生成索引,与第一次的命令参数进行匹配并得到对应的key与参数
            for idx, ret in enumerate(pipeline.execute()):
                # 取出第一次执行时对应的记录
                exec_item = exec_list[idx]
                # 如果lindex索引项有值时
                if ret:
                    if int(ret) > (now_ts - exec_item[1]):
                        # 并且与当前的时间差小于周期,则说明限定时间内次数已经达到上限了
                        break
                    else:
                        # 虽然有值,但该值已经过期,可以插入新的时间戳
                        sec_exec_list.append(('rpop', exec_item[0]))
                        sec_exec_list.append(('lpush', exec_item[0], exec_item[1]))
                else:
                    sec_exec_list.append(('lpush', exec_item[0], exec_item[1]))
            else:
                # 在else这里,说明没有使用break,则没有异常,执行第二次处理,并返回
                cls.process_exec(sec_exec_list)
                return False
            # 这里说明已经执行了break,则根据第二次的命令列表进行还原操作
            cls.rollback_exec(sec_exec_list)
            return True
        return False

    @classmethod
    def rollback_times(cls, prefix, kind):
        """
        如果消息通道发送失败,则回滚计次
        :param prefix: 前缀
        :param kind: 业务类型
        """
        # 取出限制配置
        conf = cls.get_limit_conf(kind)
        # 如果存在配置,则开始验证,否则返回`False`,说明没有限制
        if not conf:
            return False
        # 初始化命令记录列表
        pipeline = cls.client.pipeline()
        # 遍历配置中的限制条件
        for item in conf:
            # 先计算下周期,默认使用`秒`作为单位
            period = item[cls.VAL] * (item.get(cls.UNIT) or cls.S)
            # 格式化key
            key = cls.format_key(kind, prefix, period)
            pipeline.lpop(key)
        pipeline.execute()
        return True


class MobileVerifyCode():
    """
    手机验证码Backend
    """
    client = RedisClient.mobile_verify_code_db
    redis_key = 'MB:VF:CD:{mobile}:{kind}'

    CODE_FIELD = 'code'
    TIMES_FIELD = 'times'
    ID_FIELD = 'id'

    KEY_EXPIRE = 60 * 5
    VERIFY_TIMES = 3

    @classmethod
    def format_key(cls, mobile, kind):
        return cls.redis_key.format(mobile=mobile, kind=kind)

    @classmethod
    def get_random_code(cls):
        """
        获取随机验证码,得到4位数字字符串
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for _ in range(4):
            random_str.append(random.choice(seeds))

        return ''.join(random_str)

    @classmethod
    def get_cache_fields(cls, key, fileds):
        if isinstance(fileds, list):
            return cls.client.hmget(key, fileds)
        elif isinstance(fileds, str):
            return cls.client.hget(key, fileds)

    @classmethod
    def require_send_code(cls, mobile, kind):
        """
        请求发送验证码
        :param mobile: 手机号
        :return:
        """
        # 先判断是否限制住了
        if MobileVerifyLimit.is_limited(mobile, kind):
            return False, status.HTTP_429_TOO_MANY_REQUESTS
        # 格式化key
        key = cls.format_key(mobile, kind)
        # 先获取缓存中是否有未使用的验证码
        code = cls.get_cache_fields(key, cls.CODE_FIELD)
        if not code:
            code = cls.get_random_code()
        record = VerifyCode.add_record(mobile, code, kind)
        pipeline = cls.client.pipeline()
        pipeline.hmset(key, {
            cls.CODE_FIELD: code,
            cls.TIMES_FIELD: 0,
            cls.ID_FIELD: record.id,
        })
        pipeline.expire(key, cls.KEY_EXPIRE)
        pipeline.execute()
        # TODO 此处应该为请求第三发短信业务的功能，暂时没有免费的，直接将code返回前端
        if True:
            return True, code
        # 失败的话要rollback
        else:
            MobileVerifyLimit.rollback_times(mobile, kind)
            return False, status.HTTP_400_BAD_REQUEST

    @classmethod
    def verify_code(cls, mobile, kind, code, keep_code=False):
        """
        验证验证码
        :param mobile: 手机号
        :param kind: 业务种类
        :param code: 验证码
        :param keep_code: 是否在验证后保留,默认验证通过后删除缓存记录,`keep_code = True` 时则不删除
        :return: 是否验证通过
        """
        # 格式化key
        key = cls.format_key(mobile, kind)
        # 从缓存中获取验证码
        cache_code, record_id, tried_time = cls.get_cache_fields(key, [cls.CODE_FIELD, cls.ID_FIELD, cls.TIMES_FIELD])
        # 如果缓存中没有验证码,直接返回
        if not cache_code:
            return None
        if code == str(cache_code, encoding='utf-8'):
            if not keep_code:
                cls.client.delete(key)
                VerifyCode.update_record(record_id, tried_time)
                return status.HTTP_202_ACCEPTED
        else:
            # 验证错误,将验证次数字段加1
            times = cls.client.hincrby(key, cls.TIMES_FIELD)
            if times >= cls.VERIFY_TIMES:
                cls.client.delete(key)
                VerifyCode.update_record(record_id, times, is_verified=False)
                return status.HTTP_429_TOO_MANY_REQUESTS
            else:
                return status.HTTP_406_NOT_ACCEPTABLE
