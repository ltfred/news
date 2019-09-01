from redis import Redis

# 创建redis客户端
redis_client = Redis(decode_responses=True)


def release_news(title, content):
    """
    发布新闻
    :param title: 新闻标题
    :param content: 新闻内容
    """
    # 生成新闻id
    news_id = redis_client.incr("news_id")  
    news_key = "news:" + str(news_id)
    # 记录新闻数据到hash中
    redis_client.hmset(news_key, {
        "title": title,
        "content": content
    })
    # 设置缓存(过期)时间  7天
    redis_client.expire(news_key, 7 * 86400)
    # 将新闻保存到最新发布列表中
    redis_client.lpush("latest_news_list", news_key)
    # 裁切发布列表  只保留100条新闻
    redis_client.ltrim("latest_news_list", 0, 99)
    # 将新闻保存到新闻有序集合中
    redis_client.zadd("news_zset", {news_key: 0})


def show_latest_news():
    """获取最新的30条新闻"""
    return redis_client.lrange("latest_news_list", 0, 29)

def show_fav_news():
    """获取30条最受欢迎(点赞最多)的新闻"""
    return redis_client.zrange("news_zset", 0, 29, desc=True)  




def news_like(news_key, user_key):
    """对新闻点赞"""
    news_id = news_key.split(":")[-1]
    news_like_key = "news_like:" + news_id
    # 判断该用户是否对新闻点过赞, 没有点过赞才点赞数加1
    if redis_client.sadd(news_like_key, user_key): 
        # 让zset中的新闻的分数加1
        redis_client.zincrby("news_zset", 1, news_key)


def show_news_detail(news_key):
    """显示新闻详情"""
    keys = ['title', "content"]

    # 判断redis是否有该新闻的缓存(判断键是否存在)
    if redis_client.exists(news_key):   
        vals = redis_client.hmget(news_key, keys)
        # 字典推导式
        return {keys[index]:vals[index] for index in range(2)}

    else:
        # TODO 从mysql中取出新闻数据
        sql_data = {"title": "快下课", "content": "好的"}

        # 将数据保存到redis中缓存
        redis_client.hmset(news_key, {
            "title": sql_data["title"],
            "content": sql_data["content"]
        })
        # 设置缓存(过期)时间  7天
        redis_client.expire(news_key, 7 * 86400)

        return sql_data


if __name__ == '__main__':
    # 发布新闻
    # release_news("你好", "叔叔不约")
    # release_news("吃了吗", "没吃")
    # release_news("放学别走", "老地方见")

    # 显示最新发布列表
    news_list = show_latest_news()
    # # print(news_list)
    one_news_key = news_list[2]
    # # 点赞
    # news_like(one_news_key, "user:1")
    # news_like(one_news_key, "user:1")  # 只会点赞成功一次
    # # 显示点赞列表
    # news_like_list = show_fav_news()
    # print(news_like_list)

    # 获取新闻详情
    news_detail = show_news_detail("news:7")
    print(news_detail)



