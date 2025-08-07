from pydantic import BaseModel
from typing import Optional, List

class QueryOptionsLike(BaseModel):
    keywords: Optional[List[str]] = None
    persons: Optional[List[str]] = None
    albums: Optional[List[str]] = None
    from_date: Optional[str] = None  # ISO8601
    to_date: Optional[str] = None
    images: bool = True
    movies: bool = True
    uuid: Optional[List[str]] = None
    title: Optional[List[str]] = None
    description: Optional[List[str]] = None
    favorite: Optional[bool] = None
    hidden: Optional[bool] = None
    edited: Optional[bool] = None
    burst: Optional[bool] = None
    live: Optional[bool] = None
    portrait: Optional[bool] = None
    panorama: Optional[bool] = None
    uti: Optional[List[str]] = None
    location: Optional[bool] = None
    no_location: Optional[bool] = None
    is_reference: Optional[bool] = None
    in_album: Optional[bool] = None

class PhotoInfoExportOptions(BaseModel):
    dest: str
    filename: Optional[str] = None
    edited: bool = False
    live_photo: bool = False
    export_as_hardlink: bool = False
    overwrite: bool = False
    increment: bool = True
    sidecar_json: bool = False
    sidecar_exiftool: bool = False
    sidecar_xmp: bool = False
    use_photos_export: bool = False
    use_photokit: bool = True
    timeout: int = 120
    exiftool: bool = False
    use_albums_as_keywords: bool = False
    use_persons_as_keywords: bool = False
