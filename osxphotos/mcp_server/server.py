from mcp.server.fastmcp import FastMCP, Context
from .schemas import QueryOptionsLike, PhotoInfoExportOptions
from . import resources, tools_readonly, tools_write, prompts

mcp = FastMCP("osxphotos-mcp")

# --- Authentication ---
def auth_handler(token: str, ctx: Context) -> bool:
    """Simple bearer token authentication."""
    return ctx.server.expected_token == token

# --- Resources ---
mcp.resource("osxphotos://library/default")(resources.library_default)
mcp.resource("osxphotos://album/{uuid}")(resources.album_json)
mcp.resource("osxphotos://photo/{uuid}")(resources.photo_json)
mcp.resource("osxphotos://photo/{uuid}/thumb")(resources.photo_thumb)

# --- Tools (safe) ---
mcp.tool()(tools_readonly.list_albums)
mcp.tool()(tools_readonly.search_photos)
mcp.tool()(tools_readonly.photo_info)
mcp.tool()(tools_readonly.estimate_export)

# --- Tools (write) loaded conditionally (env/flag) ---
if tools_write.write_enabled():
    mcp.tool()(tools_write.export_photos)
    mcp.tool()(tools_write.add_keywords)
    mcp.tool()(tools_write.create_album)
    mcp.tool()(tools_write.add_to_album)
    mcp.tool()(tools_write.write_exif)
    mcp.tool()(tools_write.update_photos)
    mcp.tool()(tools_write.trash_photos)
    mcp.tool()(tools_write.remove_from_album)

# --- Prompts ---
mcp.prompt(title="Caption Helper")(prompts.caption_from_context)

mcp.prompt(title="Duplicate Review")(prompts.duplicate_review)

def run(transport: str = "stdio", host: str = None, port: int = None, token: str = None):
    """
    Runs the MCP server with the specified transport and options.

    :param transport: The transport to use ('stdio' or 'streamable-http').
    :param host: The host to bind to for HTTP transport.
    :param port: The port to bind to for HTTP transport.
    :param token: The bearer token to use for authentication.
    """
    if token:
        mcp.server.expected_token = token
        mcp.auth(auth_handler)
        
    if transport == "streamable-http":
        mcp.run(transport=transport, host=host, port=port)
    else:
        mcp.run(transport=transport)