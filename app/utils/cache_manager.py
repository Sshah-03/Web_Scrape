import json
import redis

class CacheManager:

    def __init__(self):
        try:
            self.redis = redis.Redis(host="localhost", port=6379, decode_responses=True)
            self.redis.ping()
            print("Redis cache enabled")
            self.use_redis = True
        except:
            print("Redis unavailable, using file cache")
            self.use_redis = False
            self.cache_file = "cache.json"

    def get(self, key):

        if self.use_redis:
            data = self.redis.get(key)
            return json.loads(data) if data else None

        try:
            with open(self.cache_file) as f:
                cache = json.load(f)
            return cache.get(key)
        except:
            return None


    def set(self, key, value):

        if self.use_redis:
            self.redis.setex(key, 300, json.dumps(value, default=str))
            return

        try:
            cache = {}

            try:
                with open(self.cache_file) as f:
                    cache = json.load(f)
            except:
                pass

            cache[key] = value

            with open(self.cache_file, "w") as f:
                json.dump(cache, f, indent=2)

        except:
            pass


cache_manager = CacheManager()
