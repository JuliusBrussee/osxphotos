import os
from mcp.server.fastmcp import Context
from osxphotos import PhotosDB, QueryOptions
from .schemas import QueryOptionsLike, PhotoInfoExportOptions
from typing import List

def list_albums(pattern: str | None = None, ctx: Context = None) -> list[dict]:
    """
    Lists albums, optionally filtering by a pattern.

    :param pattern: A string to filter album titles by (case-insensitive).
    :return: A list of dictionaries, each representing an album.
    """
    db = PhotosDB()
    albums = [a for a in db.album_info if (not pattern or pattern.lower() in a.title.lower())]
    return [{"uuid": a.uuid, "title": a.title} for a in albums]

def search_photos(q: QueryOptionsLike, ctx: Context) -> list[str]:
    """
    Searches for photos based on a set of query options.

    :param q: A QueryOptionsLike object with search criteria.
    :return: A list of UUIDs for the photos that match the query.
    """
    db = PhotosDB()
    query_args = q.model_dump(exclude_none=True)
    
    # Map plural schema names to singular QueryOptions names
    arg_map = {
        "keywords": "keyword",
        "persons": "person",
        "albums": "album",
        "images": "photos",
        "movies": "movies",
        "uuid": "uuid",
        "title": "title",
        "description": "description",
        "favorite": "favorite",
        "hidden": "hidden",
        "edited": "edited",
        "burst": "burst",
        "live": "live",
        "portrait": "portrait",
        "panorama": "panorama",
        "uti": "uti",
        "location": "location",
        "no_location": "no_location",
        "is_reference": "is_reference",
        "in_album": "in_album",
    }
    mapped_args = {arg_map.get(k, k): v for k, v in query_args.items()}
    
    results = db.query(QueryOptions(**mapped_args))
    return [p.uuid for p in results]

def photo_info(uuid: str, ctx: Context) -> dict:
    """
    Gets the information for a specific photo.

    :param uuid: The UUID of the photo to get information for.
    :return: A dictionary containing the photo's information.
    """
    db = PhotosDB()
    photo = db.get_photo(uuid)
    return photo.asdict() if photo else {"error": "not found", "uuid": uuid}

def estimate_export(uuids: List[str], options: PhotoInfoExportOptions, ctx: Context) -> dict:
    """
    Estimates the result of an export operation, checking for potential conflicts and total size.

    :param uuids: A list of photo UUIDs to estimate for export.
    :param options: A PhotoInfoExportOptions object with export settings.
    :return: A dictionary with the estimated results, including conflicts and total size.
    """
    db = PhotosDB()
    total_size = 0
    conflicts = []
    export_plan = []

    dest = options.dest

    for uuid in uuids:
        photo = db.get_photo(uuid)
        if not photo:
            continue

        filename = options.filename or photo.original_filename
        export_path = os.path.join(dest, filename)
        
        if os.path.exists(export_path) and not options.overwrite:
            conflicts.append(export_path)
        
        total_size += photo.original_filesize
        export_plan.append({"uuid": uuid, "path": export_path})

    return {
        "export_plan": export_plan,
        "conflicts": conflicts,
        "total_size_mb": total_size / (1024 * 1024),
    }

def list_library_structure(ctx: Context) -> dict:
    """
    Provides a complete overview of the library's folder and album hierarchy.

    :return: A nested dictionary representing the library structure.
    """
    db = PhotosDB()

    def _process_folders(folders):
        structure = {}
        for folder in folders:
            structure[folder.title] = {
                "uuid": folder.uuid,
                "albums": {album.title: {"uuid": album.uuid} for album in folder.album_info},
                "folders": _process_folders(folder.subfolders),
            }
        return structure

    return _process_folders(db.folder_info)

def get_photo_score(uuid: str, ctx: Context) -> dict:
    """
    Exposes the aesthetic scores for a photo directly.

    :param uuid: The UUID of the photo.
    :return: A dictionary containing the photo's aesthetic scores.
    """
    db = PhotosDB()
    photo = db.get_photo(uuid)
    return photo.score.asdict() if photo and photo.score else {"error": "not found or no score", "uuid": uuid}

def get_detected_text(uuid: str, ctx: Context) -> list:
    """
    Provides direct, on-demand access to the text detection engine.

    :param uuid: The UUID of the photo.
    :return: A list of (text, confidence) tuples.
    """
    db = PhotosDB()
    photo = db.get_photo(uuid)
    return photo.detected_text() if photo else [("error: not found", 0.0)]

def render_template(template_str: str, uuids: List[str], ctx: Context) -> dict:
    """
    Renders a template string for a list of photos.

    :param template_str: The template string to render.
    :param uuids: A list of photo UUIDs to render the template for.
    :return: A dictionary mapping each UUID to its rendered string.
    """
    db = PhotosDB()
    rendered = {}
    for uuid in uuids:
        photo = db.get_photo(uuid)
        if photo:
            rendered[uuid], _ = photo.render_template(template_str)
        else:
            rendered[uuid] = [f"error: photo not found: {uuid}"]
    return rendered