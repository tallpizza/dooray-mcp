"""S3-compatible uploader for Dooray body images."""

from __future__ import annotations

import datetime as dt
import hashlib
import hmac
import mimetypes
import os
import posixpath
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote, urlparse

import httpx


@dataclass(frozen=True)
class S3Config:
    """Configuration for S3-compatible object uploads."""

    bucket: str
    access_key_id: str
    secret_access_key: str
    region: str = "us-east-1"
    endpoint_url: Optional[str] = None
    public_base_url: Optional[str] = None
    prefix: str = "dooray-images"
    acl: Optional[str] = "public-read"
    cache_control: Optional[str] = "public, max-age=31536000, immutable"
    force_path_style: bool = False
    session_token: Optional[str] = None

    @classmethod
    def from_env(cls) -> "S3Config":
        endpoint_url = _empty_to_none(os.getenv("S3_ENDPOINT_URL"))
        force_path_style = _parse_bool(
            os.getenv("S3_FORCE_PATH_STYLE"),
            default=bool(endpoint_url),
        )

        config = cls(
            bucket=os.getenv("S3_BUCKET", "").strip(),
            access_key_id=(os.getenv("S3_ACCESS_KEY_ID") or os.getenv("AWS_ACCESS_KEY_ID") or "").strip(),
            secret_access_key=(os.getenv("S3_SECRET_ACCESS_KEY") or os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip(),
            region=(os.getenv("S3_REGION") or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1").strip(),
            endpoint_url=endpoint_url,
            public_base_url=_empty_to_none(os.getenv("S3_PUBLIC_BASE_URL")),
            prefix=os.getenv("S3_PREFIX", "dooray-images").strip(),
            acl=_parse_acl(os.getenv("S3_ACL")),
            cache_control=_empty_to_none(os.getenv("S3_CACHE_CONTROL")) or "public, max-age=31536000, immutable",
            force_path_style=force_path_style,
            session_token=_empty_to_none(os.getenv("S3_SESSION_TOKEN") or os.getenv("AWS_SESSION_TOKEN")),
        )
        config.validate()
        return config

    def validate(self) -> None:
        missing = []
        if not self.bucket:
            missing.append("S3_BUCKET")
        if not self.access_key_id:
            missing.append("S3_ACCESS_KEY_ID or AWS_ACCESS_KEY_ID")
        if not self.secret_access_key:
            missing.append("S3_SECRET_ACCESS_KEY or AWS_SECRET_ACCESS_KEY")
        if not self.region:
            missing.append("S3_REGION or AWS_REGION")

        if missing:
            raise ValueError("Missing S3 configuration: " + ", ".join(missing))


class S3Uploader:
    """Upload files to S3 using Signature Version 4 without extra dependencies."""

    def __init__(self, config: S3Config, transport: Optional[httpx.AsyncBaseTransport] = None):
        self.config = config
        self._transport = transport

    async def upload_file(
        self,
        file_path: str,
        *,
        filename: Optional[str] = None,
        content_type: Optional[str] = None,
        key: Optional[str] = None,
    ) -> Dict[str, Any]:
        path = Path(file_path).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"File not found: {path}")

        object_filename = filename or path.name
        object_key = key or self._make_object_key(object_filename)
        upload_content_type = content_type or mimetypes.guess_type(object_filename)[0] or "application/octet-stream"
        content = path.read_bytes()

        upload_url, canonical_uri = self._upload_url_and_canonical_uri(object_key)
        public_url = self._public_url(object_key)
        headers = self._signed_headers(
            canonical_uri=canonical_uri,
            content=content,
            content_type=upload_content_type,
            extra_headers=self._extra_headers(),
        )

        async with httpx.AsyncClient(transport=self._transport, timeout=60.0) as client:
            response = await client.put(upload_url, content=content, headers=headers)

        if response.status_code < 200 or response.status_code >= 300:
            raise Exception(f"S3 upload failed: {response.status_code} {response.text}")

        return {
            "url": public_url,
            "markdown": f"![{object_filename}]({public_url})",
            "html": f'<img src="{public_url}" alt="{object_filename}">',
            "bucket": self.config.bucket,
            "key": object_key,
            "filename": object_filename,
            "mimeType": upload_content_type,
            "size": len(content),
            "etag": response.headers.get("etag"),
        }

    def _make_object_key(self, filename: str) -> str:
        today = dt.datetime.now(dt.timezone.utc).strftime("%Y/%m/%d")
        safe_filename = _safe_filename(filename)
        prefix = self.config.prefix.strip("/")
        generated_name = f"{uuid.uuid4().hex}-{safe_filename}"
        if prefix:
            return posixpath.join(prefix, today, generated_name)
        return posixpath.join(today, generated_name)

    def _endpoint_url(self) -> str:
        return (self.config.endpoint_url or f"https://s3.{self.config.region}.amazonaws.com").rstrip("/")

    def _upload_url_and_canonical_uri(self, key: str) -> tuple[str, str]:
        endpoint = self._endpoint_url()
        parsed = urlparse(endpoint)
        encoded_key = _quote_key(key)
        base_path = parsed.path.rstrip("/")

        if self.config.force_path_style:
            canonical_uri = f"{base_path}/{self.config.bucket}/{encoded_key}"
            return f"{parsed.scheme}://{parsed.netloc}{canonical_uri}", canonical_uri

        host = f"{self.config.bucket}.{parsed.netloc}"
        canonical_uri = f"{base_path}/{encoded_key}"
        return f"{parsed.scheme}://{host}{canonical_uri}", canonical_uri

    def _public_url(self, key: str) -> str:
        encoded_key = _quote_key(key)
        if self.config.public_base_url:
            return f"{self.config.public_base_url.rstrip('/')}/{encoded_key}"

        endpoint = self._endpoint_url()
        parsed = urlparse(endpoint)
        base_path = parsed.path.rstrip("/")
        if self.config.force_path_style:
            return f"{parsed.scheme}://{parsed.netloc}{base_path}/{self.config.bucket}/{encoded_key}"

        return f"{parsed.scheme}://{self.config.bucket}.{parsed.netloc}{base_path}/{encoded_key}"

    def _extra_headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if self.config.acl:
            headers["x-amz-acl"] = self.config.acl
        if self.config.cache_control:
            headers["cache-control"] = self.config.cache_control
        if self.config.session_token:
            headers["x-amz-security-token"] = self.config.session_token
        return headers

    def _signed_headers(
        self,
        *,
        canonical_uri: str,
        content: bytes,
        content_type: str,
        extra_headers: Dict[str, str],
    ) -> Dict[str, str]:
        now = dt.datetime.now(dt.timezone.utc)
        amz_date = now.strftime("%Y%m%dT%H%M%SZ")
        date_stamp = now.strftime("%Y%m%d")
        payload_hash = hashlib.sha256(content).hexdigest()
        host = urlparse(self._upload_url_and_canonical_uri("placeholder")[0]).netloc

        headers = {
            "content-type": content_type,
            "host": host,
            "x-amz-content-sha256": payload_hash,
            "x-amz-date": amz_date,
            **{k.lower(): v for k, v in extra_headers.items()},
        }

        signed_header_names = sorted(headers)
        canonical_headers = "".join(f"{name}:{_normalize_header_value(headers[name])}\n" for name in signed_header_names)
        signed_headers = ";".join(signed_header_names)
        canonical_request = "\n".join([
            "PUT",
            canonical_uri,
            "",
            canonical_headers,
            signed_headers,
            payload_hash,
        ])

        credential_scope = f"{date_stamp}/{self.config.region}/s3/aws4_request"
        string_to_sign = "\n".join([
            "AWS4-HMAC-SHA256",
            amz_date,
            credential_scope,
            hashlib.sha256(canonical_request.encode("utf-8")).hexdigest(),
        ])
        signing_key = _signature_key(self.config.secret_access_key, date_stamp, self.config.region, "s3")
        signature = hmac.new(signing_key, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        headers["authorization"] = (
            "AWS4-HMAC-SHA256 "
            f"Credential={self.config.access_key_id}/{credential_scope}, "
            f"SignedHeaders={signed_headers}, "
            f"Signature={signature}"
        )
        return headers


def _signature_key(secret_key: str, date_stamp: str, region: str, service: str) -> bytes:
    key = ("AWS4" + secret_key).encode("utf-8")
    date_key = hmac.new(key, date_stamp.encode("utf-8"), hashlib.sha256).digest()
    region_key = hmac.new(date_key, region.encode("utf-8"), hashlib.sha256).digest()
    service_key = hmac.new(region_key, service.encode("utf-8"), hashlib.sha256).digest()
    return hmac.new(service_key, b"aws4_request", hashlib.sha256).digest()


def _safe_filename(filename: str) -> str:
    name = Path(filename).name or "image"
    return re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip(".-") or "image"


def _quote_key(key: str) -> str:
    return "/".join(quote(part, safe="") for part in key.split("/"))


def _normalize_header_value(value: str) -> str:
    return " ".join(str(value).strip().split())


def _empty_to_none(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _parse_bool(value: Optional[str], *, default: bool = False) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _parse_acl(value: Optional[str]) -> Optional[str]:
    if value is None:
        return "public-read"
    normalized = value.strip()
    if normalized.lower() in {"", "none", "false", "disabled", "off"}:
        return None
    return normalized
