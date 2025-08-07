from mcp.server.fastmcp import Context
from osxphotos import PhotosDB
from .schemas import QueryOptionsLike
import re
import json


def caption_from_context(uuid: str, style: str = "plain", ctx: Context = None) -> str:
    """
    Generates a prompt for an AI to create a caption for a photo based on its context.

    :param uuid: The UUID of the photo.
    :param style: The desired style of the caption (e.g., 'plain', 'travel', 'journal').
    :return: A string containing the generated prompt.
    """
    db = PhotosDB()
    photo = db.get_photo(uuid)

    if not photo:
        return f"Error: Photo with UUID {uuid} not found."

    context = []
    if photo.title:
        context.append(f"- Title: {photo.title}")
    if photo.description:
        context.append(f"- Description: {photo.description}")
    if photo.persons:
        context.append(f"- People: {', '.join(photo.persons)}")
    if photo.place:
        context.append(f"- Location: {photo.place.name}")
    if photo.keywords:
        context.append(f"- Keywords: {', '.join(photo.keywords)}")

    try:
        detected_text = photo.detected_text()
        if detected_text:
            text = [item[0] for item in detected_text]
            context.append(f"- Detected Text: {', '.join(text)}")
    except Exception:
        # Ignore errors if text detection is not available
        pass

    prompt = f"Generate a {style} caption for a photo with the following context:\n"
    prompt += "\n".join(context)

    return prompt





def duplicate_review(uuids: list[str], ctx: Context = None) -> dict:
    """
    Finds potential duplicates for a given list of photos and returns a structured
    response for an AI to guide the user through a review process.

    :param uuids: A list of photo UUIDs to check for duplicates.
    :return: A dictionary containing sets of potential duplicates.
    """
    db = PhotosDB()
    duplicate_sets = {}

    for uuid in uuids:
        photo = db.get_photo(uuid)
        if not photo:
            continue

        duplicates = photo.duplicates
        if duplicates:
            # Use a frozenset of UUIDs as a key to group duplicate sets
            dup_set_key = frozenset([p.uuid for p in duplicates] + [uuid])
            if dup_set_key not in duplicate_sets:
                duplicate_sets[dup_set_key] = {
                    "original": photo.uuid,
                    "duplicates": [p.uuid for p in duplicates],
                    "recommendation": "Suggest user review and then use the `trash_photos` tool on the duplicates."
                }

    # Convert the dictionary to a list of duplicate sets for the final output
    return {"duplicate_sets": list(duplicate_sets.values())}
