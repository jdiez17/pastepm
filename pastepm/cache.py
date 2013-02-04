from pastepm.database import using_redis, r
from functools import wraps, partial
import hashlib

def memoize(f=None, time=0):
    if f == None:
        return partial(memoize, time=time)

    @wraps(f)
    def wrap(*args, **kwargs):
        if using_redis:
            h = hashlib.sha1()
            h.update(str(type(args[0])) + str(kwargs))
            key = "pastepm.cache.%s" % h.hexdigest()

            if r.exists(key):
                return r.get(key)
            else:
                result = f(*args, **kwargs)
                if time > 0:
                    r.setex(key, time, result)
                else:
                    r.set(key, result)

                return result
        else:
            return f(*args, **kwargs)

    return wrap
