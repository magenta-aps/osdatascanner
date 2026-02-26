from os import getenv
from time import time
from flask import Flask, request, Response, make_response
from parse import parse
from urllib.parse import urljoin
from sqlalchemy import select, MetaData, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from dataclasses import field, dataclass
import cryptography.fernet as fernet
import mimetypes
from functools import wraps

DDI_TABLES = ("DokumentDataInfo", "DokumentDataTypeOpslag", "Kladde")
DRAFT_TABLES = ("Kladde",)

app = Flask(__name__)
key = fernet.Fernet.generate_key()
cryptctx = fernet.Fernet(key)
expiry = int(getenv("DP_TOKEN_LIFETIME", "3600"))


@dataclass
class CacheEntry:
    db_str: str
    connection: Engine = field(compare=False)
    metadata: MetaData = field(compare=False)


cache = []
cache_size = 10


def open_connection(db_str, tables):
    global cache

    ce: CacheEntry | None = None
    for idx, ce in enumerate(cache):
        if ce.db_str == db_str:
            cache.pop(idx)
            break
    else:
        engine = create_engine(db_str)
        metadata = MetaData()
        metadata.reflect(bind=engine, only=tables)

        cache.append(ce := CacheEntry(db_str, engine, metadata))

    cache.append(ce)
    cache = cache[-cache_size:]
    return (ce.connection, ce.metadata)


def decompose_client_id(cid: str):
    user = host = port = database = None
    if pr := parse("{user}@{host}:{port}/{database}", cid):
        user, host, port, database = pr.named.values()
    elif pr := parse("{user}@{host}/{database}", cid):
        user, host, database = pr.named.values()
        port = 1433
    else:
        raise ValueError
    return (user, host, int(port), database)


@app.route(
        "/sbsys.document/token",
        methods=["POST"])
def make_token():
    match request.form:
        case {"grant_type": "client_credentials",
              "client_id": client_id,
              "client_secret": client_secret}:
            try:
                user, host, port, database = decompose_client_id(client_id)
            except ValueError:
                return (dict(error="invalid_client"), 400, [])
            conn_str = (
                    "mssql+pymssql://"
                    f"{user}:{client_secret}@{host}:{port}/{database}")

            return {
                "token_type": "Bearer",
                "expires_in": expiry - 1,
                "access_token": cryptctx.encrypt(conn_str.encode()).decode()
            }
        case {"grant_type": x} if x != "client_credentials":
            return (dict(error="unsupported_grant_type"), 400, [])
        case _:
            return (dict(error="invalid_request"), 400, [])


def get_auth_token():
    match request.headers.get("Authorization", "").split(" "):
        case ["Bearer", token]:
            return token
        case _:
            return None


__unspecified = object()


def token_valid(token: str = __unspecified) -> str | bool:
    if token is __unspecified:
        token = get_auth_token()
    if not token:
        return "No token specified"
    try:
        ts = cryptctx.extract_timestamp(token.encode())
        if time() > ts + expiry:
            return "Valid token has expired"
        else:
            return True
    except fernet.InvalidToken:
        return "Invalid token"


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_auth_token()
        if isinstance(error := token_valid(token), str):
            return (f"{error} :|", 401)

        conn_str = cryptctx.decrypt(token.encode()).decode()
        return f(conn_str, *args, **kwargs)
    return decorated_function


@app.route(
        "/sbsys.document/test_token",
        methods=["POST"])
def test_token():
    if isinstance(error := token_valid(), str):
        return (f"{error} :|", 401)
    else:
        return (":D", 200)


def make_response2(*args, **kwargs):
    match args:
        case (body, int() as status, dict() as headers):
            response = Response(body, status, headers)
            for flag, value in kwargs.items():
                setattr(response, flag, value)
            return response
        case _:
            return make_response(*args)


def get_ddi(
        engine,
        metadata,
        document_pk: int,
        ddi_pk: int | None = None):
    DokumentDataInfo = metadata.tables["DokumentDataInfo"]
    DokumentDataTypeOpslag = metadata.tables["DokumentDataTypeOpslag"]
    query = select().add_columns(
            DokumentDataInfo.c.ID, DokumentDataInfo.c.AlternateOfID,
            DokumentDataInfo.c.FileName, DokumentDataInfo.c.FileExtension,
            DokumentDataInfo.c.FileSize, DokumentDataInfo.c.IsDeleted,
            DokumentDataTypeOpslag.c.Navn)

    if ddi_pk:
        query = query.where(DokumentDataInfo.c.ID == ddi_pk)

    with Session(engine) as session:
        result = session.execute(query.where(
                DokumentDataInfo.c.DokumentID == document_pk,
                DokumentDataInfo.c.DokumentDataType == (
                        DokumentDataTypeOpslag.c.ID)))
        match ddi_pk:
            case None:
                return [r._asdict() for r in result]
            case int():
                rv = result.first()
                if rv is not None:
                    return rv._asdict()
                else:
                    return None


def get_draft(engine, metadata, draft_pk: int):
    Draft = metadata.tables["Kladde"]
    query = select().add_columns(
            Draft.c.ID, Draft.c.FileName, Draft.c.FileExtension,
            Draft.c.FileSize, Draft.c.DeletedState)

    with Session(engine) as session:
        result = session.execute(query.where(Draft.c.ID == draft_pk)).first()
        return result._asdict() if result else None


TYPE_NAME_MAPPING = {
    "Microsoft Word": "application/msword",
    ("Microsoft Word", ".docx"):
    "application/vnd.openxmlformats-officedocument"
    ".wordprocessingml.document",

    "Microsoft Excel": "application/vnd.ms-excel",
    ("Microsoft Excel", ".xlsx"):
    "application/vnd.openxmlformats-officedocument"
    ".spreadsheetml.sheet",

    "Microsoft PowerPoint": "application/vnd.ms-powerpoint",
    ("Microsoft PowerPoint", ".pptx"):
    "application/vnd.openxmlformats-officedocument"
    ".presentationml.presentation",

    "Tekst": "text/plain",
    "RTF": "text/rtf",
    "PDF": "application/pdf",

    ("Billede", ".jpg"): "image/jpeg",
    ("Billede", ".jpeg"): "image/jpeg",
    ("Billede", ".png"): "image/png",
    ("Billede", ".bmp"): "image/x-ms-bmp",

    # Film Klip
    # Lyd

    "HTML": "text/html",
    ("Email", ".eml"): "message/rfc822",
}


def type_name_label_to_mime_type(
        file_extension: str, type_name: str) -> str:
    file_extension = "." + file_extension.lower().lstrip(".")
    if mime_type := TYPE_NAME_MAPPING.get((type_name, file_extension,)):
        return mime_type
    elif mime_type := TYPE_NAME_MAPPING.get(type_name):
        return mime_type
    else:
        return "application/octet-stream"


def extension_to_mime_type(file_extension: str) -> str:
    """Guess mime type for file extension.
    Used for drafts, as there isn't a lookup table like DokumentDataTypeOpslag for Dokumenter """
    if not file_extension:
        return "application/octet-stream"

    if not file_extension.startswith('.'):
        file_extension = f".{file_extension}"

    # guess_type expects a filename, but it isn't really relevant, so we call it dummy_name.
    mime_type, _ = mimetypes.guess_type(f"dummy_name{file_extension}")
    return mime_type or "application/octet-stream"


@app.route(
        "/sbsys.document/<int:doc_id>",
        methods=["GET"])
@token_required
def list_ddis(conn_str, doc_id):
    engine, metadata = open_connection(conn_str, DDI_TABLES)

    code = 500
    response = {
        "status": "error",
        "message": "unknown error"
    }
    headers = {}
    match get_ddi(engine, metadata, doc_id):
        case []:
            code = 404
            response = {
                "status": "error",
                "message": "no document data found"
            }
        case [*objects]:
            code = 200
            response = {
                "status": "ok",
                "values": (v := [])
            }
            for obj in objects:
                v.append({
                    "id": obj["ID"],
                    "name": f"{obj['FileName']}{obj['FileExtension']}",
                    "size": obj["FileSize"],
                    "mime_type": type_name_label_to_mime_type(
                        obj["FileExtension"], obj["Navn"]
                    ),

                    "alternate_of": obj["AlternateOfID"],
                    "is_deleted": obj["IsDeleted"],

                    "path": (path := f"{doc_id}/{obj['ID']}"),
                    "content_link": urljoin(
                            request.host_url,
                            f"sbsys.document/{path}/$value"),
                })
    return make_response((response, code, headers))


@app.route(
        "/sbsys.document/<int:doc_id>/<int:ddi_id>",
        methods=["HEAD"])
@token_required
def get_metadata(conn_str, doc_id: int, ddi_id: int):
    engine, metadata = open_connection(conn_str, DDI_TABLES)

    match get_ddi(engine, metadata, doc_id, ddi_id):
        case None:
            return (":|", 404)  # Not Found
        case {"IsDeleted": True}:
            return (":|", 410)  # Gone
        case {"FileExtension": extension, "Navn": type_name, "FileSize": size}:
            mime_type = type_name_label_to_mime_type(extension, type_name)

            return make_response2(
                    None, 200,
                    {
                        "Content-Type": mime_type,
                        "Content-Length": str(size)
                    },
                    automatically_set_content_length=False)


@app.route(
        "/sbsys.document/<int:doc_id>/<int:ddi_id>/$value",
        methods=["GET"])
@token_required
def get_content(conn_str, doc_id: int, ddi_id: int):
    engine, metadata = open_connection(conn_str, DDI_TABLES)

    match get_ddi(engine, metadata, doc_id, ddi_id):
        case None:
            return (":|", 404)  # Not Found
        case {"IsDeleted": True}:
            return (":|", 410)  # Gone
        case {"FileExtension": extension, "Navn": type_name}:
            mime_type = type_name_label_to_mime_type(extension, type_name)

            doc_group = doc_id // 25_000
            doc_conn_str = conn_str + f"Dokument{doc_group:04d}"

            doc_db, doc_md = open_connection(doc_conn_str, ("DokumentData",))

            DokumentData = doc_md.tables["DokumentData"]
            query = select().add_columns(DokumentData.c.Data,)

            with Session(doc_db) as session:
                content = session.execute(query.where(
                        DokumentData.c.DokumentID == doc_id,
                        DokumentData.c.DokumentDataInfoID == ddi_id)).first()

            match content:
                case None:
                    return (";(", 404)  # Not Found
                case (data,):
                    return (data, {"Content-Type": mime_type})


@app.route(
        "/sbsys.document/draft/<int:draft_id>",
        methods=["GET"])
@token_required
def list_draft(conn_str, draft_id):
    engine, metadata = open_connection(conn_str, DRAFT_TABLES)

    meta = get_draft(engine, metadata, draft_id)
    if not meta:
        return make_response(({"status": "error", "message": "no draft found"}, 404, {}))

    v = [{
        "id": meta["ID"],
        "name": f"{meta['FileName']}{meta['FileExtension']}",
        "size": meta["FileSize"],
        "mime_type": extension_to_mime_type(meta["FileExtension"]),
        "alternate_of": None,
        "is_deleted": meta["DeletedState"] != 0,
        "path": f"draft/{draft_id}/file",
        "content_link": urljoin(
            request.host_url,
            f"sbsys.document/draft/{draft_id}/file/$value")
    }]
    return make_response(({"status": "ok", "values": v}, 200, {}))


@app.route(
        "/sbsys.document/draft/<int:draft_id>/file",
        methods=["HEAD"])
@token_required
def head_draft_metadata(conn_str, draft_id: int):
    engine, metadata = open_connection(conn_str, DRAFT_TABLES)

    meta = get_draft(engine, metadata, draft_id)
    if not meta:
        return (":|", 404)
    if meta["DeletedState"] != 0:
        return (":|", 410)

    mime_type = extension_to_mime_type(meta["FileExtension"])
    return make_response2(
            None, 200,
            {
                "Content-Type": mime_type,
                "Content-Length": str(meta["FileSize"])
            },
            automatically_set_content_length=False)


@app.route(
        "/sbsys.document/draft/<int:draft_id>/file/$value",
        methods=["GET"])
@token_required
def get_draft_content(conn_str, draft_id: int):
    engine, metadata = open_connection(conn_str, DRAFT_TABLES)

    meta = get_draft(engine, metadata, draft_id)
    if not meta:
        return (":|", 404)
    if meta["DeletedState"] != 0:
        return (":|", 410)

    mime_type = extension_to_mime_type(meta["FileExtension"])

    draft_group = draft_id // 25_000
    draft_conn_str = conn_str + f"Kladde{draft_group:04d}"

    draft_db, draft_md = open_connection(draft_conn_str, ("KladdeData",))
    DraftData = draft_md.tables["KladdeData"]

    query = select().add_columns(DraftData.c.Data)

    with Session(draft_db) as session:
        content = session.execute(query.where(
                DraftData.c.KladdeID == draft_id)
        ).first()
    match content:
        case None:
            return (";(", 404)
        case (data,):
            return (data, {"Content-Type": mime_type})
