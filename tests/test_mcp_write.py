import unittest
from unittest.mock import patch, MagicMock

from osxphotos.mcp_server import tools_write


class TestMcpWrite(unittest.TestCase):
    @patch("osxphotos.mcp_server.tools_write.photoscript")
    @patch.dict("os.environ", {"OSXPHOTOS_MCP_ALLOW_WRITE": "1"})
    def test_update_photos(self, mock_photoscript):
        """Test that update_photos correctly calls photoscript."""
        mock_photo = MagicMock()
        mock_photoscript.Photo.return_value = mock_photo

        tools_write.update_photos(
            uuids=["uuid1"],
            title="New Title",
            description="New Description",
            favorite=True,
            add_keywords=["new_keyword"],
            remove_keywords=["old_keyword"],
            date="2025-08-07T12:00:00",
            ctx=None,
        )

        mock_photoscript.Photo.assert_called_with("uuid1")
        self.assertEqual(mock_photo.title, "New Title")
        self.assertEqual(mock_photo.description, "New Description")
        self.assertTrue(mock_photo.favorite)
        self.assertEqual(mock_photo.keywords, ["new_keyword"])
        self.assertEqual(mock_photo.date, mock_photoscript.utils.datetime_from_iso_str("2025-08-07T12:00:00"))

    @patch("osxphotos.mcp_server.tools_write.photoscript")
    @patch.dict("os.environ", {"OSXPHOTOS_MCP_ALLOW_WRITE": "1"})
    def test_trash_photos(self, mock_photoscript):
        """Test that trash_photos correctly calls photoscript."""
        mock_photo = MagicMock()
        mock_photoscript.Photo.return_value = mock_photo

        tools_write.trash_photos(uuids=["uuid1"], ctx=None)

        mock_photoscript.Photo.assert_called_with("uuid1")
        mock_photo.delete.assert_called_once()

    @patch("osxphotos.mcp_server.tools_write.photoscript")
    @patch.dict("os.environ", {"OSXPHOTOS_MCP_ALLOW_WRITE": "1"})
    def test_remove_from_album(self, mock_photoscript):
        """Test that remove_from_album correctly calls photoscript."""
        mock_album = MagicMock()
        mock_photoscript.Album.return_value = mock_album
        mock_photo = MagicMock()
        mock_photoscript.Photo.return_value = mock_photo

        tools_write.remove_from_album(
            album_uuid="album1", photo_uuids=["photo1"], ctx=None
        )

        mock_photoscript.Album.assert_called_with("album1")
        mock_album.remove.assert_called_once_with([mock_photo])

    @patch("osxphotos.mcp_server.tools_write.photoscript")
    @patch.dict("os.environ", {"OSXPHOTOS_MCP_ALLOW_WRITE": "1"})
    def test_create_folder(self, mock_photoscript):
        """Test that create_folder correctly calls photoscript."""
        mock_library = MagicMock()
        mock_photoscript.PhotosLibrary.return_value = mock_library

        tools_write.create_folder(name="New Folder", ctx=None)

        mock_library.create_folder.assert_called_once_with("New Folder")

    @patch("osxphotos.mcp_server.tools_write.photoscript")
    @patch.dict("os.environ", {"OSXPHOTOS_MCP_ALLOW_WRITE": "1"})
    def test_set_album_keyphoto(self, mock_photoscript):
        """Test that set_album_keyphoto correctly calls photoscript."""
        mock_album = MagicMock()
        mock_photoscript.Album.return_value = mock_album
        mock_photo = MagicMock()
        mock_photoscript.Photo.return_value = mock_photo

        tools_write.set_album_keyphoto(
            album_uuid="album1", photo_uuid="photo1", ctx=None
        )

        mock_photoscript.Album.assert_called_with("album1")
        mock_album.set_keyphoto.assert_called_once_with(mock_photo)

    @patch.dict("os.environ", {"OSXPHOTOS_MCP_ALLOW_WRITE": "0"})
    def test_write_disabled(self):
        """Test that write operations are disabled by default."""
        result = tools_write.update_photos(uuids=["uuid1"], title="New Title", ctx=None)
        self.assertEqual(result, {"error": "write operations not enabled"})


if __name__ == "__main__":
    unittest.main()
