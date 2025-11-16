import os
import random
import time

import msgpack
import requests
from locust import FastHttpUser, task
from locust.exception import RescheduleTask

URL_PREFIX = "http://localhost/api/v1"
FILE_PATH = "load_testing/test_file.txt"


class CloudStorageUser(FastHttpUser):
    def on_start(self):
        random_id = random.randint(1, 100_000_000)
        username = f"test{random_id}"

        self.client.post(
            f"{URL_PREFIX}/auth/register",
            data=self._pack(
                {
                    "username": username,
                    "email": f"t{random_id}es{random_id}t@mail.ru",
                    "password": "test_password",
                }
            ),
        )

        response = self.client.post(
            f"{URL_PREFIX}/auth/log-in",
            data=self._pack({"username": username, "password": "test_password"}),
        )
        self._set_creds(self._unpack(response))

    def on_stop(self):
        self.client.delete(f"{URL_PREFIX}/auth/profile", headers=self.headers)

    @task(10)
    def auth(self):
        self.client.get(f"{URL_PREFIX}/auth", headers=self.headers)

    @task(7)
    def refresh_token(self):
        response = self.client.post(
            f"{URL_PREFIX}/auth/refresh-tokens",
            data=self._pack({"refresh_token": self.refresh_token}),
            headers=self.headers,
        )
        self._set_creds(self._unpack(response))

    @task(3)
    def profile_info(self):
        self.client.get(f"{URL_PREFIX}/auth/profile", headers=self.headers)

    @task(2)
    def session_list(self):
        self.client.get(f"{URL_PREFIX}/auth/sessions", headers=self.headers)

    @task(10)
    def list_files(self):
        self.client.get(f"{URL_PREFIX}/files", headers=self.headers)

    @task(5)
    def file_info(self):
        files = self._get_files()
        if not files:
            return
        first_id = files[0]["file_id"]
        self.client.get(f"{URL_PREFIX}/files/{first_id}", headers=self.headers)

    @task(4)
    def delete_file(self):
        files = self._get_files()
        if not files:
            return
        first_id = files[0]["file_id"]
        self.client.delete(
            f"{URL_PREFIX}/files?file_id={first_id}", headers=self.headers
        )

    @task(5)
    def upload_file(self):
        file_name = str(random.randint(1, 100_000_000))
        file_size = os.path.getsize(FILE_PATH)

        response = self.client.post(
            f"{URL_PREFIX}/files/upload/initiate",
            data=self._pack({"name": file_name, "size": file_size}),
            headers=self.headers,
        )
        data = self._unpack(response)

        upload_id = data["upload_id"]
        part_size = data["part_size"]
        parts = data["parts"]

        results = []
        for part in parts:
            start = (part["part_number"] - 1) * part_size
            res = self._upload_part(
                FILE_PATH, part["url"], part["part_number"], start, part_size
            )
            results.append(res)

        results.sort(key=lambda x: x["part_number"])
        payload = {"upload_id": upload_id, "parts": results}

        self.client.post(
            f"{URL_PREFIX}/files/upload/complete",
            data=self._pack(payload),
            headers=self.headers,
        )

    @task(5)
    def download_file(self):
        files = self._get_files()
        if not files:
            return
        first_id = files[0]["file_id"]
        response = self.client.get(
            f"{URL_PREFIX}/files/download/{first_id}",
            headers=self.headers,
            allow_redirects=False,
        )
        if response.headers:
            presigned_url = response.headers.get("Location", "")
            self.client.get(f"http://localhost{presigned_url}", stream=True)

    def _upload_part(self, file_path, url, part_number, start, size):
        with open(file_path, "rb") as f:
            f.seek(start)
            data = f.read(size)

        full_url = f"http://localhost{url}"
        start_time = time.time()

        try:
            response = requests.put(full_url, data=data, timeout=60)
            response.raise_for_status()
            etag = response.headers.get("ETag", "").strip('"')
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="PUT",
                name=full_url,
                response_time=total_time,
                response_length=len(data),
                response=response,
            )
            return {"part_number": part_number, "etag": etag}
        except Exception as e:
            total_time = int((time.time() - start_time) * 1000)
            self.environment.events.request.fire(
                request_type="PUT",
                name=full_url,
                response_time=total_time,
                response_length=0,
                exception=e,
            )
            raise RescheduleTask(f"Upload failed for part {part_number}: {e}")

    def _get_files(self):
        response = self.client.get(f"{URL_PREFIX}/files", headers=self.headers)
        return self._unpack(response).get("files", [])

    def _set_creds(self, data):
        self.headers = {
            "Authorization": f"Bearer {data['access_token']}",
            "Content-Type": "application/x-msgpack",
        }
        self.refresh_token = data["refresh_token"]

    @staticmethod
    def _pack(data):
        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def _unpack(response):
        return msgpack.unpackb(response.content, raw=False)
