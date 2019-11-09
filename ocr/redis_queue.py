
import redis

REDIS_IP="localhost"
REDIS_PORT="6379"
REDIS_DB="2"






class Redis_Queue:
    QUEUE_NAME="queue"
    def __init__(self,ip=REDIS_IP,port=REDIS_PORT,db=REDIS_DB):
        self.redis_ = redis.Redis(host=ip, port=port, db=db, decode_responses=True)

    def set_item(self,item):
        self.redis_.lpush(self.QUEUE_NAME,item)

    def queue_run(self,f=None,skip_first=False):
        """
        循环执行传入方法
        :param f: 被执行的方法，要求返回True或者False，来表示是否执行成功，只有当方法返回True的时候，才会将数据冲队列中弹出
        :return:
        """
        if f==None:
            return
        if skip_first:
            self.redis_.rpush(self.QUEUE_NAME, self.redis_.lpop(self.QUEUE_NAME))
        while (self.redis_.llen(self.QUEUE_NAME)>0):
            item=self.redis_.lindex(self.QUEUE_NAME,0)
            r=f(item)
            if r:
                self.redis_.lpop(self.QUEUE_NAME)
            else:
                self.redis_.rpush(self.QUEUE_NAME,self.redis_.lpop(self.QUEUE_NAME))


def f(item):
    print(item)
    return True


if __name__ == '__main__':
    q=Redis_Queue()
    # for i in range(10):
    #     q.set_item(i)
    q.queue_run(f)
    # print(redis_.keys())



