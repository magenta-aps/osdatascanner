from os import getenv
from time import time
from flask import Flask, request, Response, make_response
from parse import parse
from sqlalchemy import select, MetaData, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.engine import Engine
from dataclasses import field, dataclass
import cryptography.fernet as fernet


DDI_TABLES = ("DokumentDataInfo", "DokumentDataTypeOpslag",)


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


def get_ddi(engine, metadata, document_pk: int):
    DokumentDataInfo = metadata.tables["DokumentDataInfo"]
    DokumentDataTypeOpslag = metadata.tables["DokumentDataTypeOpslag"]
    query = select().add_columns(
            DokumentDataInfo.c.FileName, DokumentDataInfo.c.FileExtension,
            DokumentDataInfo.c.FileSize, DokumentDataInfo.c.IsDeleted,
            DokumentDataTypeOpslag.c.Navn)

    with Session(engine) as session:
        result = session.execute(query.where(
                DokumentDataInfo.c.DokumentID == document_pk,
                DokumentDataInfo.c.DokumentDataType == (
                        DokumentDataTypeOpslag.c.ID)))
        return result.first()


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


@app.route(
        "/sbsys.document/<int:pk>",
        methods=["HEAD"])
def get_metadata(pk: int):
    if isinstance(error := token_valid(token := get_auth_token()), str):
        return (f"{error} :|", 401)

    conn_str = cryptctx.decrypt(token).decode()
    engine, metadata = open_connection(conn_str, DDI_TABLES)

    match get_ddi(engine, metadata, pk):
        case None:
            return (":|", 404)  # Not Found
        case (_, _, _, True, _):
            return (":|", 410)  # Gone
        case (name, extension, size, False, type_name):
            return make_response2(
                    None, 200,
                    {
                        "Content-Type": type_name_label_to_mime_type(
                                extension, type_name),
                        "Content-Disposition":
                        "attachment;"
                        f" filename={name}{extension}",
                        "Content-Length": str(size)
                    },
                    automatically_set_content_length=False)


@app.route(
        "/sbsys.document/<int:pk>",
        methods=["GET"])
def get_content(pk: int):
    if isinstance(error := token_valid(token := get_auth_token()), str):
        return (f"{error} :|", 401)

    conn_str = cryptctx.decrypt(token).decode()

    engine, metadata = open_connection(conn_str, DDI_TABLES)

    match get_ddi(engine, metadata, pk):
        case None:
            return (":|", 404)  # Not Found
        case (_, _, _, True, _):
            return (":|", 410)  # Gone
        case (name, extension, size, False, type_name):
            document_group = pk // 25_000
            doc_conn_str = conn_str + f"Dokument{document_group:04d}"

            doc_db, doc_md = open_connection(doc_conn_str, ("DokumentData",))

            DokumentData = doc_md.tables["DokumentData"]
            query = select().add_columns(DokumentData.c.Data,)

            with Session(doc_db) as session:
                content = session.execute(query.where(
                        DokumentData.c.DokumentID == pk)).first()

            match content:
                case None:
                    return (";(", 404)  # Not Found
                case (data,):
                    return (data, 200, {
                        "Content-Type": type_name_label_to_mime_type(
                                extension, type_name),
                        "Content-Disposition":
                        "attachment;"
                        f" filename={name}{extension}",
                        "Content-Length": str(size)
                    })
