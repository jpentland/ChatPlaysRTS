class RegexError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class TomlError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class AuthenticationError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ConnectionFailedError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class ClientDisconnectError(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
