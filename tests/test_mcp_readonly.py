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


if __name__ == "__main__":
    unittest.main()
