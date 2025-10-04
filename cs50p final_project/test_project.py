import unittest
import io
from tkinter import *

from PIL import Image, ImageTk
from unittest.mock import patch, Mock
import project


class TestApod(unittest.TestCase):
    def setUp(self):
        project.apod_pack = []  # Reset list
        project.CURRENT_INDEX = 0

    @patch('requests.get')
    @patch('project.messagebox')
    @patch('project.date_entry.get')
    @patch('project.api_entry.get')
    def test_get_apod(self, mock_api_entry, mock_date_entry, mock_messagebox, mock_get):
        mock_date_entry.return_value = '2024-11-30'
        mock_api_entry.return_value = 'MOCK_KEY'

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'date': mock_date_entry.get(),
            'explanation': 'Explanation',
            'media_type': 'image',
            'url': 'http://example.com/image.png',
            'title': 'Title'
        }

        # Create a simple in-memory image to mock image data
        image = Image.new("RGB", (100, 100), color="red")
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        mock_image_data = buffer.getvalue()

        mock_get.side_effect = [
            mock_response,  # First response: API JSON
            Mock(content=mock_image_data)  # Second response: valid image content
        ]

        result = project.get_apod()

        # Assert the result
        self.assertIsNotNone(result)
        self.assertEqual(len(project.apod_pack), 1)
        self.assertIn('Title', result[1])
        self.assertIn('Explanation', result[2])

        # Check that no warning messages were shown
        mock_messagebox.showinfo.assert_not_called()
        mock_messagebox.showwarning.assert_not_called()
        mock_messagebox.showerror.assert_not_called()

    @patch('project.requests.get')
    @patch('project.messagebox')
    @patch('project.date_entry.get')
    @patch('project.api_entry.get')
    def test_get_apod_with_non_image(self, mock_api_entry, mock_date_entry, mock_messagebox, mock_get):
        """Test the function with a non-image media response."""
        mock_date_entry.return_value = '2024-11-30'
        mock_api_entry.return_value = 'FAKE_API_KEY'

        # Mock API response with a non-image media type
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'url': 'http://example.com/video.mp4',
            'media_type': 'video',
            'title': 'Test Video',
            'explanation': 'This is a video, not an image.'
        }
        mock_get.return_value = mock_response

        result = project.get_apod()
        self.assertIsNone(result)  # Function should return None for non-image media
        mock_messagebox.showinfo.assert_called_with(
            title="No Image",
            message="No image available for the selected date."
        )

    def test_date_is_valid(self):
        self.assertTrue(project.date_is_valid('2020-10-10'))
        self.assertFalse(project.date_is_valid('2020/10/10'))
        self.assertFalse(project.date_is_valid('wrong date'))
        self.assertFalse(project.date_is_valid('2019-02-29'))

    @patch('project.display_photo_on_canvas')
    def test_show_next_image(self, mock_display_photo):
        project.apod_pack = [('image', 'text', 'explanation'), ('image2', 'text2', 'explanation2')]
        project.show_next_image()
        self.assertEqual(project.CURRENT_INDEX, 1)
        mock_display_photo.assert_called_once()

    def test_with_no_next_img(self):
        project.CURRENT_INDEX = len(project.apod_pack) - 1
        project.show_next_image()
        self.assertEqual(project.CURRENT_INDEX, len(project.apod_pack) - 1)

    @patch('project.display_photo_on_canvas')
    def test_show_previous_image(self, mock_display_photo):
        project.CURRENT_INDEX = 1
        project.apod_pack = [('image', 'text', 'explanation'), ('image2', 'text2', 'explanation2')]
        project.show_previous_image()
        self.assertEqual(project.CURRENT_INDEX, 0)
        mock_display_photo.assert_called_once()

    def test_with_no_previous(self):
        project.show_previous_image()
        self.assertEqual(project.CURRENT_INDEX, 0)


    if __name__ == '__main__':
        unittest.main()
