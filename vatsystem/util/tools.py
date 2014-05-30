# -*- coding: utf-8 -*-

__all__ = ["partial","OrderedSet","Bunch"]

def partial(*args, **create_time_kwds):
    func = args[0]
    create_time_args = args[1:]
    def curried_function(*call_time_args, **call_time_kwds):
        args = create_time_args + call_time_args
        kwds = create_time_kwds.copy()
        kwds.update(call_time_kwds)
        return func(*args, **kwds)
    return curried_function



class OrderedSet(list):
    """Set preserving item order."""

    def add(self, item):
        if item not in self:
            self.append(item)

    def add_all(self, iterable):
        for item in iterable:
            self.add(item)
            
            
class Bunch(dict):
    """A dictionary that provides attribute-style access."""

    def __getitem__(self, key):
        return  dict.__getitem__(self, key)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            return get_partial_dict(name, self)

    __setattr__ = dict.__setitem__

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)
            