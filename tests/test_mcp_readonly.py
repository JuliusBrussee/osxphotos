import unittest
from unittest.mock import patch, MagicMock

from osxphotos.mcp_server import tools_readonly, prompts
from osxphotos.mcp_server.schemas import QueryOptionsLike


class TestMcpReadonly(unittest.TestCase):
    @patch("osxphotos.mcp_server.tools_readonly.PhotosDB")
    def test_search_photos_favorite(self, mock_photosdb):
        """Test that search_photos correctly handles the favorite parameter."""
        mock_db_instance = MagicMock()
        mock_photosdb.return_value = mock_db_instance

        query = QueryOptionsLike(favorite=True)
        tools_readonly.search_photos(query, ctx=None)

        mock_db_instance.query.assert_called_once()
        called_args, _ = mock_db_instance.query.call_args
        self.assertTrue(called_args[0].favorite)

    @patch("osxphotos.mcp_server.tools_readonly.PhotosDB")
    def test_search_photos_hidden(self, mock_photosdb):
        """Test that search_photos correctly handles the hidden parameter."""
        mock_db_instance = MagicMock()
        mock_photosdb.return_value = mock_db_instance

        query = QueryOptionsLike(hidden=True)
        tools_readonly.search_photos(query, ctx=None)

        mock_db_instance.query.assert_called_once()
        called_args, _ = mock_db_instance.query.call_args
        self.assertTrue(called_args[0].hidden)

    @patch("osxphotos.mcp_server.prompts.PhotosDB")
    def test_duplicate_review(self, mock_photosdb):
        """Test that duplicate_review returns a structured plan."""
        mock_photo = MagicMock()
        mock_photo.uuid = "uuid1"
        mock_duplicate = MagicMock()
        mock_duplicate.uuid = "uuid2"
        mock_photo.duplicates = [mock_duplicate]

        mock_db_instance = MagicMock()
        mock_db_instance.get_photo.return_value = mock_photo
        mock_photosdb.return_value = mock_db_instance

        result = prompts.duplicate_review(["uuid1"], ctx=None)

        self.assertIn("duplicate_sets", result)
        self.assertEqual(len(result["duplicate_sets"]), 1)
        dup_set = result["duplicate_sets"][0]
        self.assertEqual(dup_set["original"], "uuid1")
        self.assertEqual(dup_set["duplicates"], ["uuid2"])
        self.assertEqual(
            dup_set["recommendation"],
            "Suggest user review and then use the `trash_photos` tool on the duplicates.",
        )

    @patch("osxphotos.mcp_server.tools_readonly.PhotosDB")
    def test_list_library_structure(self, mock_photosdb):
        """Test that list_library_structure returns a nested dictionary."""
        mock_album = MagicMock()
        mock_album.title = "Test Album"
        mock_album.uuid = "album1"

        mock_folder = MagicMock()
        mock_folder.title = "Test Folder"
        mock_folder.uuid = "folder1"
        mock_folder.album_info = [mock_album]
        mock_folder.subfolders = []

        mock_db_instance = MagicMock()
        mock_db_instance.folder_info = [mock_folder]
        mock_photosdb.return_value = mock_db_instance

        result = tools_readonly.list_library_structure(ctx=None)

        self.assertIn("Test Folder", result)
        self.assertIn("Test Album", result["Test Folder"]["albums"])

    @patch("osxphotos.mcp_server.tools_readonly.PhotosDB")
    def test_get_photo_score(self, mock_photosdb):
        """Test that get_photo_score returns the score of a photo."""
        mock_score = MagicMock()
        mock_score.asdict.return_value = {"overall": 0.8}

        mock_photo = MagicMock()
        mock_photo.score = mock_score

        mock_db_instance = MagicMock()
        mock_db_instance.get_photo.return_value = mock_photo
        mock_photosdb.return_value = mock_db_instance

        result = tools_readonly.get_photo_score("uuid1", ctx=None)

        self.assertEqual(result, {"overall": 0.8})

    @patch("osxphotos.mcp_server.tools_readonly.PhotosDB")
    def test_get_detected_text(self, mock_photosdb):
        """Test that get_detected_text returns the detected text of a photo."""
        mock_photo = MagicMock()
        mock_photo.detected_text.return_value = [("Hello", 0.9)]

        mock_db_instance = MagicMock()
        mock_db_instance.get_photo.return_value = mock_photo
        mock_photosdb.return_value = mock_db_instance

        result = tools_readonly.get_detected_text("uuid1", ctx=None)

        self.assertEqual(result, [("Hello", 0.9)])

    @patch("osxphotos.mcp_server.tools_readonly.PhotosDB")
    def test_render_template(self, mock_photosdb):
        """Test that render_template returns the rendered template of a photo."""
        mock_photo = MagicMock()
        mock_photo.render_template.return_value = (["rendered_template"], [])

        mock_db_instance = MagicMock()
        mock_db_instance.get_photo.return_value = mock_photo
        mock_photosdb.return_value = mock_db_instance

        result = tools_readonly.render_template("{template}", ["uuid1"], ctx=None)

        self.assertEqual(result, {"uuid1": ["rendered_template"]})


if __name__ == "__main__":
    unittest.main()
