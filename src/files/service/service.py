from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

import proto
from config import load_config
from controllers import DatabaseController as DBC
from controllers import StorageController as STC
from proto import files_pb2 as pb2
from utils import ExceptionHandler


class FilesServicer(proto.FilesServicer):
    _eh = ExceptionHandler(load_config().app.logger)

    async def UploadFile(self, request_iterator, context):
        file_data = await self._eh(context, STC.upload_file, request_iterator)
        await self._eh(context, DBC.upload_file, file_data)
        return pb2.Empty()

    async def FileInfo(self, request, context):
        data = self.convert_to_dict(request)
        info = await self._eh(context, DBC.file_info, data)
        return pb2.FileInfoResponse(**info)

    async def FileList(self, request, context):
        files = await self._eh(context, DBC.file_list, request.user_id)
        return pb2.FileListResponse(
            files=(pb2.FileInfoResponse(**file) for file in files)
        )

    async def DownloadFile(self, request, context):
        data = self.convert_to_dict(request)
        info = await self._eh(context, DBC.file_info, data)
        data["name"] = info["name"]
        file_url = await self._eh(context, STC.download_file, data)
        return pb2.FileURLResponse(url=file_url)

    async def DeleteFiles(self, request, context):
        data = self.convert_to_dict(request)
        filenames = await self._eh(context, DBC.delete_files, data)
        await self._eh(context, STC.delete_files, filenames)
        return pb2.Empty()

    async def DeleteAllFiles(self, request, context):
        await self._eh(context, STC.delete_all_files, request.user_id)
        await self._eh(context, DBC.delete_all_files, request.user_id)
        return pb2.Empty()

    @staticmethod
    def convert_to_dict(data: Message) -> dict:
        return MessageToDict(data, preserving_proto_field_name=True)
