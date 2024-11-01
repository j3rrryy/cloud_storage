from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers

DESCRIPTOR: _descriptor.FileDescriptor

class AccessToken(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class AuthResponse(_message.Message):
    __slots__ = ("user_id", "verified")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    verified: bool
    def __init__(self, user_id: _Optional[str] = ..., verified: bool = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class LogInResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token", "email", "browser", "verified")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    BROWSER_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    email: str
    browser: str
    verified: bool
    def __init__(
        self,
        access_token: _Optional[str] = ...,
        refresh_token: _Optional[str] = ...,
        email: _Optional[str] = ...,
        browser: _Optional[str] = ...,
        verified: bool = ...,
    ) -> None: ...

class LogInRequest(_message.Message):
    __slots__ = ("username", "password", "user_ip", "user_agent")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USER_IP_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    username: str
    password: str
    user_ip: str
    user_agent: str
    def __init__(
        self,
        username: _Optional[str] = ...,
        password: _Optional[str] = ...,
        user_ip: _Optional[str] = ...,
        user_agent: _Optional[str] = ...,
    ) -> None: ...

class ProfileResponse(_message.Message):
    __slots__ = ("user_id", "username", "email", "verified", "registered")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    REGISTERED_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    username: str
    email: str
    verified: bool
    registered: str
    def __init__(
        self,
        user_id: _Optional[str] = ...,
        username: _Optional[str] = ...,
        email: _Optional[str] = ...,
        verified: bool = ...,
        registered: _Optional[str] = ...,
    ) -> None: ...

class RefreshRequest(_message.Message):
    __slots__ = ("refresh_token", "user_ip", "user_agent")
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USER_IP_FIELD_NUMBER: _ClassVar[int]
    USER_AGENT_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    user_ip: str
    user_agent: str
    def __init__(
        self,
        refresh_token: _Optional[str] = ...,
        user_ip: _Optional[str] = ...,
        user_agent: _Optional[str] = ...,
    ) -> None: ...

class RegisterRequest(_message.Message):
    __slots__ = ("username", "email", "password")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    username: str
    email: str
    password: str
    def __init__(
        self,
        username: _Optional[str] = ...,
        email: _Optional[str] = ...,
        password: _Optional[str] = ...,
    ) -> None: ...

class RevokeSessionRequest(_message.Message):
    __slots__ = ("access_token", "session_id")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    session_id: str
    def __init__(
        self, access_token: _Optional[str] = ..., session_id: _Optional[str] = ...
    ) -> None: ...

class Sessions(_message.Message):
    __slots__ = ("sessions",)
    SESSIONS_FIELD_NUMBER: _ClassVar[int]
    sessions: _containers.RepeatedCompositeFieldContainer[SessionInfo]
    def __init__(
        self, sessions: _Optional[_Iterable[_Union[SessionInfo, _Mapping]]] = ...
    ) -> None: ...

class SessionInfo(_message.Message):
    __slots__ = ("session_id", "user_ip", "browser", "last_accessed")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    USER_IP_FIELD_NUMBER: _ClassVar[int]
    BROWSER_FIELD_NUMBER: _ClassVar[int]
    LAST_ACCESSED_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    user_ip: str
    browser: str
    last_accessed: str
    def __init__(
        self,
        session_id: _Optional[str] = ...,
        user_ip: _Optional[str] = ...,
        browser: _Optional[str] = ...,
        last_accessed: _Optional[str] = ...,
    ) -> None: ...

class Tokens(_message.Message):
    __slots__ = ("access_token", "refresh_token")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    def __init__(
        self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ...
    ) -> None: ...

class UpdateEmailRequest(_message.Message):
    __slots__ = ("access_token", "new_email")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NEW_EMAIL_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    new_email: str
    def __init__(
        self, access_token: _Optional[str] = ..., new_email: _Optional[str] = ...
    ) -> None: ...

class UpdatePasswordRequest(_message.Message):
    __slots__ = ("access_token", "old_password", "new_password")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    OLD_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    NEW_PASSWORD_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    old_password: str
    new_password: str
    def __init__(
        self,
        access_token: _Optional[str] = ...,
        old_password: _Optional[str] = ...,
        new_password: _Optional[str] = ...,
    ) -> None: ...

class UserId(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class VerificationMail(_message.Message):
    __slots__ = ("verification_token", "username", "email")
    VERIFICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    verification_token: str
    username: str
    email: str
    def __init__(
        self,
        verification_token: _Optional[str] = ...,
        username: _Optional[str] = ...,
        email: _Optional[str] = ...,
    ) -> None: ...

class VerificationToken(_message.Message):
    __slots__ = ("verification_token",)
    VERIFICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    verification_token: str
    def __init__(self, verification_token: _Optional[str] = ...) -> None: ...
