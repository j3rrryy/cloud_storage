from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

import proto
from config import load_config
from controllers import DatabaseController as DBC
from proto import auth_pb2 as pb2
from utils import ExceptionHandler


class AuthServicer(proto.AuthServicer):
    _eh = ExceptionHandler(load_config().app.logger)

    async def Register(self, request, context):
        data = self.convert_to_dict(request)
        verification_mail = await self._eh(context, DBC.register, data)
        if verification_mail:
            return pb2.VerificationMail(**verification_mail)

    async def VerifyEmail(self, request, context):
        await self._eh(context, DBC.verify_email, request.verification_token)
        return pb2.Empty()

    async def RequestResetCode(self, request, context):
        reset_mail = await self._eh(context, DBC.request_reset_code, request.email)
        if reset_mail:
            return pb2.ResetCodeResponse(**reset_mail)

    async def ValidateResetCode(self, request, context):
        data = self.convert_to_dict(request)
        is_valid = await self._eh(context, DBC.validate_reset_code, data)
        if is_valid is not None:
            return pb2.CodeIsValid(is_valid=is_valid)

    async def ResetPassword(self, request, context):
        data = self.convert_to_dict(request)
        await self._eh(context, DBC.reset_password, data)
        return pb2.Empty()

    async def LogIn(self, request, context):
        data = self.convert_to_dict(request)
        login_data = await self._eh(context, DBC.log_in, data)
        if login_data:
            return pb2.LogInResponse(**login_data)

    async def LogOut(self, request, context):
        await self._eh(context, DBC.log_out, request.access_token)
        return pb2.Empty()

    async def ResendVerificationMail(self, request, context):
        verification_mail = await self._eh(
            context, DBC.resend_verification_mail, request.access_token
        )
        if verification_mail:
            return pb2.VerificationMail(**verification_mail)

    async def Auth(self, request, context):
        user_info = await self._eh(context, DBC.auth, request.access_token)
        if user_info:
            return pb2.AuthResponse(**user_info)

    async def Refresh(self, request, context):
        data = self.convert_to_dict(request)
        tokens = await self._eh(context, DBC.refresh, data)
        if tokens:
            return pb2.Tokens(**tokens)

    async def SessionList(self, request, context):
        sessions = await self._eh(context, DBC.session_list, request.access_token)
        if sessions:
            return pb2.Sessions(
                sessions=(pb2.SessionInfo(**session) for session in sessions)
            )

    async def RevokeSession(self, request, context):
        data = self.convert_to_dict(request)
        await self._eh(context, DBC.revoke_session, data)
        return pb2.Empty()

    async def Profile(self, request, context):
        profile = await self._eh(context, DBC.profile, request.access_token)
        if profile:
            return pb2.ProfileResponse(**profile)

    async def UpdateEmail(self, request, context):
        data = self.convert_to_dict(request)
        verification_mail = await self._eh(context, DBC.update_email, data)
        if verification_mail:
            return pb2.VerificationMail(**verification_mail)

    async def UpdatePassword(self, request, context):
        data = self.convert_to_dict(request)
        await self._eh(context, DBC.update_password, data)
        return pb2.Empty()

    async def DeleteProfile(self, request, context):
        user_id = await self._eh(context, DBC.delete_profile, request.access_token)
        if user_id:
            return pb2.UserId(user_id=user_id)

    @staticmethod
    def convert_to_dict(data: Message) -> dict:
        return MessageToDict(data, preserving_proto_field_name=True)
