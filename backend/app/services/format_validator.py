"""模型文件格式校验：扩展名、魔数、大小、ZIP 路径安全（概要 4.4.1 / 4.4.3）。"""
import io
import json
import os
import zipfile

from dataclasses import dataclass

# 与概要设计一致：单文件最大 500MB
MAX_UPLOAD_BYTES = 500 * 1024 * 1024
ALLOWED_EXTENSIONS = frozenset({".xmi", ".xml", ".json", ".zip"})


class FormatValidationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


@dataclass
class ValidatedPayload:
    """解压 ZIP 后或原始文件的有效载荷。"""
    content: bytes
    logical_name: str
    original_ext: str


def _ext_from_name(name: str) -> str:
    return os.path.splitext(name)[1].lower()


def _magic_zip(head: bytes) -> bool:
    return len(head) >= 4 and head[:2] == b"PK"


def _magic_json(head: bytes) -> bool:
    s = head.lstrip()[:1]
    return s in (b"{", b"[")


def _magic_xml(head: bytes) -> bool:
    t = head.lstrip()[:200].lower()
    return b"<xml" in t or b"<?xml" in t or b"<xmi" in t


def validate_extension(filename: str) -> str:
    ext = _ext_from_name(filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise FormatValidationError(
            f"不支持的文件类型：{ext or '(无扩展名)'}，允许：{', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    return ext


def validate_size(content: bytes) -> None:
    if len(content) > MAX_UPLOAD_BYTES:
        raise FormatValidationError(
            f"文件过大：{len(content)} 字节，上限 {MAX_UPLOAD_BYTES // (1024 * 1024)} MB"
        )


def _zip_entry_is_safe(name: str) -> bool:
    if not name or name.startswith("/"):
        return False
    parts = name.replace("\\", "/").split("/")
    if any(p == ".." for p in parts):
        return False
    return True


def _extract_zip_payload(zf: zipfile.ZipFile) -> tuple[bytes, str]:
    """从 ZIP 中选取主模型文件（优先 .xmi，其次 .xml，再 .json）。"""
    names = [n for n in zf.namelist() if not n.endswith("/") and _zip_entry_is_safe(n)]
    if not names:
        raise FormatValidationError("ZIP 内无有效文件")

    def score(n: str) -> tuple[int, str]:
        ext = _ext_from_name(n)
        pri = {".xmi": 0, ".xml": 1, ".json": 2}.get(ext, 99)
        return (pri, n)

    candidates = [n for n in names if _ext_from_name(n) in (".xmi", ".xml", ".json")]
    if not candidates:
        raise FormatValidationError("ZIP 内未找到 .xmi / .xml / .json 模型文件")
    chosen = sorted(candidates, key=score)[0]
    with zf.open(chosen, "r") as fp:
        data = fp.read()
    return data, chosen


def validate_and_load_payload(filename: str, content: bytes) -> ValidatedPayload:
    """
    校验原始字节并返回待解析内容。
    ZIP：校验成员路径，解压出单个主模型文件内容。
    """
    validate_size(content)
    ext = validate_extension(filename)
    head = content[:4096]

    if ext == ".zip":
        if not _magic_zip(head):
            raise FormatValidationError("ZIP 文件头无效")
        try:
            zf = zipfile.ZipFile(io.BytesIO(content))
        except zipfile.BadZipFile as e:
            raise FormatValidationError(f"ZIP 损坏或无法读取：{e}") from e
        with zf:
            inner, inner_name = _extract_zip_payload(zf)
        validate_size(inner)
        inner_ext = _ext_from_name(inner_name)
        if inner_ext not in (".xmi", ".xml", ".json"):
            raise FormatValidationError("ZIP 内主文件扩展名无效")
        ih = inner[:4096]
        if inner_ext == ".json" and not _magic_json(ih):
            raise FormatValidationError("ZIP 内 JSON 内容无效")
        if inner_ext in (".xmi", ".xml") and not _magic_xml(ih):
            raise FormatValidationError("ZIP 内 XML/XMI 内容无效")
        return ValidatedPayload(content=inner, logical_name=inner_name, original_ext=ext)

    if ext == ".json":
        if not _magic_json(head):
            raise FormatValidationError("JSON 文件应以 { 或 [ 开头")
        try:
            json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            raise FormatValidationError(f"JSON 解析失败：{e}") from e
        return ValidatedPayload(content=content, logical_name=filename, original_ext=ext)

    if not _magic_xml(head):
        raise FormatValidationError("XML/XMI 文件应以 <?xml 或 <xml/<xmi 开头")
    return ValidatedPayload(content=content, logical_name=filename, original_ext=ext)


def validate_stream_meta(filename: str, total_size: int) -> str:
    """在上传前仅校验扩展名与声明大小（分片上传汇总前）。"""
    ext = validate_extension(filename)
    if total_size > MAX_UPLOAD_BYTES:
        raise FormatValidationError(
            f"文件过大：声明 {total_size} 字节，上限 {MAX_UPLOAD_BYTES // (1024 * 1024)} MB"
        )
    return ext
