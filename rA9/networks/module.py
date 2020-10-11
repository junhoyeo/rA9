from collections import OrderedDict


class Module(object):
    def __init__(self):
        self._parameters = OrderedDict()
        self._modules = OrderedDict()
        self.training = True

    def forward(self, *input):
        raise NotImplementedError

    def register_parameter(self, name, param):
        if param is None:
            self._parameters[name] = None
        else:
            self._parameters[name] = param

    def add_module(self, name, module):
        if hasattr(self, name):
            raise KeyError('attribute already exists '{}''.format(name))
        if not isinstance(module, Module) and module is not None:
            raise TypeError('This is not a Module subclass')
        self._modules[name] = module

    def _apply(self, fn):
        for module in self.children():
            module._apply(fn)

        for param in self.array:  # 검증 A
            if param is not None:
                param = fn(param)
        for key, buf in self._buffers.items():
            if buf is not None:
                self._buffers[key] = fn(buf)

        return self

    def __call__(self, *input, **kwargs):

        result = self.forward(*input, **kwargs)

        return result

    # TODO: override without breaking default behavior
    # https://stackoverflow.com/questions/2405590/how-do-i-override-getattr-in-python-without-breaking-the-default-behavior

    # def __getattr__(self, name):
    #     print(self.__dict__)
    #     print(self._parameters)
    #     if '_parameters' in self.__dict__:
    #         _parameters = self.__dict__['_parameters']
    #         if name in _parameters:
    #             return _parameters[name]
    #     if '_buffers' in self.__dict__:
    #         _buffers = self.__dict__['_buffers']
    #         if name in _buffers:
    #             return _buffers[name]
    #     if '_modules' in self.__dict__:
    #         modules = self.__dict__['_modules']
    #         if name in modules:
    #             return modules[name]
    #     raise AttributeError(''{}' object has no attribute '{}''.format(
    #         type(self).__name__, name))

    # def __setattr__(self, name, value):
    #     if params is not None:
    #         self.register_parameter(name, value)
    #     else:
    #         modules = self.__dict__.get('_modules')
    #         if isinstance(value, Module):
    #             if modules is None:
    #                 raise AttributeError('cannot assign module before Module.__init__() call')
    #             modules[name] = value
    #         elif modules is not None and name in modules:
    #             modules[name] = value
    #         else:
    #             buffers = self.__dict__.get('_buffers')
    #             if buffers is not None and name in buffers:
    #                 buffers[name] = value
    #             else:
    #                 object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in self._parameters:
            del self._parameters[name]
        elif name in self._buffers:
            del self._buffers[name]
        elif name in self._modules:
            del self._modules[name]
        else:
            object.__delattr__(self, name)

    def parameters(self):
        for name, param in self.named_parameters():
            yield param

    def named_parameters(self, memo=None, prefix=''):
        if memo is None:
            memo = set()
        for name, p in self._parameters.items():
            if p is not None and p not in memo:
                memo.add(p)
                yield prefix + ('.' if prefix else '') + name, p
        for mname, module in self.named_children():
            submodule_prefix = prefix + ('.' if prefix else '') + mname
            for name, p in module.named_parameters(memo, submodule_prefix):
                yield name, p

    def children(self):
        for name, module in self.named_children():
            yield module

    def named_children(self):
        memo = set()
        for name, module in self._modules.items():
            if module is not None and module not in memo:
                memo.add(module)
                yield name, module

    def modules(self):
        for name, module in self.named_modules():
            yield module

    def named_modules(self, memo=None, prefix=''):

        if memo is None:
            memo = set()
        if self not in memo:
            memo.add(self)
            yield prefix, self
            for name, module in self._modules.items():
                if module is None:
                    continue
                submodule_prefix = prefix + ('.' if prefix else '') + name
                for m in module.named_modules(memo, submodule_prefix):
                    yield m

    def train(self, mode=True):

        self.training = mode
        for module in self.children():
            module.train(mode)
        return self

    def eval(self):

        return self.train(False)
