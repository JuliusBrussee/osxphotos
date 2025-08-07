# osxphotos MCP Server: AI Integration

This document provides a detailed overview of the Model Context Protocol (MCP) server implementation within `osxphotos`. It explains the architecture, features, and usage of the new AI integration capabilities.

## 1. Introduction: Why MCP?

The Model Context Protocol (MCP) is an open standard that allows AI assistants, like the Gemini CLI and VS Code Copilot Chat, to connect to and interact with external tools and data sources. By integrating an MCP server into `osxphotos`, we have unlocked the ability to control the Photos library using natural language.

Users can now ask an AI to perform complex tasks like "export all my photos from 2023 with the keyword 'vacation' to a folder on my desktop," and the AI will use the `osxphotos` MCP server to execute these commands.

## 2. Core Implementation Details

The MCP server is built on the `mcp` Python library, which provides the `FastMCP` server implementation. The server is designed to be a lightweight wrapper around the existing `osxphotos` and `photoscript` APIs, ensuring that we reuse as much of the existing, well-tested code as possible.

### 2.1. File Structure

The MCP server implementation is contained within the `osxphotos/mcp_server/` directory, which includes the following key files:

-   `server.py`: The main entry point for the MCP server. It defines the server, registers all the resources, tools, and prompts, and handles the server lifecycle.
-   `resources.py`: Implements the MCP resources, which provide read-only access to the Photos library's data, such as the library info, albums, and photos.
-   `tools_readonly.py`: Contains all the read-only tools, such as `list_albums`, `search_photos`, and `photo_info`.
-   `tools_write.py`: Contains all the write-enabled tools, such as `export_photos`, `add_keywords`, and `create_album`. These tools are only available when the server is run with the `--allow-write` flag.
-   `prompts.py`: Implements the MCP prompts, which are templates that guide the AI in performing multi-step tasks, such as generating a caption for a photo or reviewing duplicates.
-   `schemas.py`: Defines the Pydantic models used for data validation and serialization in the MCP tools and resources.

### 2.2. CLI Integration

A new command, `osxphotos mcp-server`, has been added to the main `osxphotos` CLI. This command is the primary way to launch the MCP server. It includes the following options:

-   `--allow-write`: Enables the write-enabled tools, which are disabled by default for safety.
-   `--http`: Runs the server over HTTP, allowing it to be accessed by a wider range of clients.
-   `--token-env`: Specifies an environment variable that contains a bearer token for authentication when running over HTTP.

### 2.3. Dependencies

The MCP server introduces two new dependencies, which are managed as an optional extra in `pyproject.toml`:

-   `mcp[cli]`: The core MCP library for building the server.
-   `photoscript`: A library for interacting with the Photos app's AppleScript interface, used for all write operations to ensure safe and reliable modifications to the Photos library.

## 3. Features in Detail

The `osxphotos` MCP server exposes a rich set of features, categorized into resources, tools, and prompts.

### 3.1. Resources

Resources provide a way for the AI to browse the Photos library's data without making any changes. The following resources are implemented:

-   `osxphotos://library/default`: Returns metadata about the default Photos library, including its path, version, and photo/album counts.
-   `osxphotos://album/{uuid}`: Returns detailed information about a specific album, including its title and a list of the photo UUIDs it contains.
-   `osxphotos://photo/{uuid}`: Returns the full `PhotoInfo.asdict()` for a specific photo, providing a comprehensive set of metadata.
-   `osxphotos://photo/{uuid}/thumb`: Returns a thumbnail image for a specific photo.

### 3.2. Read-Only Tools

These tools allow the AI to query and retrieve information from the Photos library:

-   `list_albums(pattern: str|None)`: Lists all albums, with an option to filter by a text pattern.
-   `search_photos(query: QueryOptionsLike)`: A powerful tool that allows the AI to search for photos using a rich set of query options, mirroring the `osxphotos.query()` method.
-   `photo_info(uuid: str)`: Retrieves the detailed metadata for a single photo.
-   `estimate_export(uuids: list[str], options: PhotoInfoExportOptions)`: A dry-run tool that estimates the results of an export operation, including a list of files to be exported, potential filename conflicts, and the total size of the export.
-   `list_library_structure()`: Provides a complete overview of the library's folder and album hierarchy.
-   `get_photo_score(uuid: str)`: Exposes the aesthetic scores for a photo directly.
-   `get_detected_text(uuid: str)`: Provides direct, on-demand access to the text detection engine.
-   `render_template(template_str: str, uuids: list[str])`: Renders a template string for a list of photos.

### 3.3. Write-Enabled Tools

These tools, which are only active when the `--allow-write` flag is used, allow the AI to make changes to the Photos library:

-   `export_photos(uuids: list[str], options: PhotoInfoExportOptions)`: Exports photos to a specified destination on disk. This tool is implemented asynchronously to handle long-running exports and provides progress and cancellation support.
-   `update_photos(uuids: list[str], title: str, description: str, favorite: bool, add_keywords: list[str], remove_keywords: list[str], date: str)`: A unified tool to update photo metadata.
-   `add_keywords(uuids: list[str], keywords: list[str])`: Adds keywords to a set of photos.
-   `create_album(title: str)`: Creates a new album in the Photos library.
-   `add_to_album(album_uuid: str, uuids: list[str])`: Adds a set of photos to an existing album.
-   `remove_from_album(album_uuid: str, photo_uuids: list[str])`: Removes photos from an album.
-   `trash_photos(uuids: list[str])`: Moves photos to the "Recently Deleted" album.
-   `write_exif(uuids: list[str], fields: dict)`: Writes EXIF data to a set of photos using `osxphotos`' built-in ExifTool integration.
-   `create_folder(name: str, parent_uuid: str)`: Creates a new folder in Photos.
-   `set_album_keyphoto(album_uuid: str, photo_uuid: str)`: Sets the key photo for an album.

### 3.4. Prompts

Prompts are a unique feature of MCP that allow the server to guide the AI through complex, multi-step tasks. The following prompts are implemented:

-   `caption_from_context(uuid: str, style: str)`: This prompt takes a photo's UUID and a desired caption style (e.g., "plain", "travel", "journal"). It then extracts a rich set of context from the photo, including its title, description, people, location, keywords, and any detected text. It then formats this context into a prompt that it sends to the AI, asking it to generate a caption in the specified style.
-   `duplicate_review(uuids: list[str])`: This prompt takes a list of photo UUIDs and uses the `PhotoInfo.duplicates` property to find potential duplicates. It then returns a structured list of duplicate sets to the AI, which can then present them to the user for review and action (e.g., deleting duplicates or adding them to an album).

## 4. Security and Safety

Security was a primary consideration in the design of the MCP server. The following measures have been implemented to ensure the safety of the user's Photos library:

-   **Default Read-Only Mode:** The server starts in a read-only mode by default. All tools that can modify the Photos library or the user's file system are disabled.
-   **Explicit Write-Enablement:** To enable the write tools, the user must explicitly pass the `--allow-write` flag when starting the server. This ensures that no accidental modifications can be made.
-   **Use of `photoscript` for Write Operations:** All modifications to the Photos library are performed using the `photoscript` library, which uses the official AppleScript interface to interact with the Photos app. This is the safest and most reliable way to make changes to the library.
-   **Bearer Token Authentication:** When running in HTTP mode, the server can be configured to require a bearer token for authentication, preventing unauthorized access.
-   **Path Traversal Prevention:** The `export_photos` tool resolves the destination path to prevent path traversal attacks, and error messages have been made more generic to avoid leaking sensitive information.

## 5. How to Use the MCP Server

To use the `osxphotos` MCP server, you first need to install the necessary dependencies:

```bash
pip install "osxphotos[mcp]"
```

Then, you can run the server from the command line:

```bash
# Run in read-only mode
osxphotos mcp-server

# Run with write-access enabled
osxphotos mcp-server --allow-write
```

To connect to the server from an AI client like the Gemini CLI, you will need to create a `settings.json` file in your `~/.gemini/` directory with the following content:

```json
{
  "mcpServers": {
    "osxphotos": {
      "command": "python3",
      "args": [
        "-m",
        "osxphotos",
        "mcp-server",
        "--allow-write"
      ],
      "env": {
        "OSXPHOTOS_MCP_TOKEN": "your_secret_token_here"
      }
    }
  }
}
```

Once the server is running and configured, you can start interacting with it from your AI client using natural language.