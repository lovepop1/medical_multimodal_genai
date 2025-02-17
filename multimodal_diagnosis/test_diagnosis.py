import unittest
from unittest.mock import patch, MagicMock
import os
import logging
from diagnosis_helper import *

class Test(unittest.TestCase):
    def testing_image_analysis(self):
        log_groClient = run_setup()
        logger=log_groClient[0]
        groq_client=log_groClient[1]
        analysis_result=analyze_image(os.path.join('temp_images','temp_img.png'), logger)
        self.assertNotEqual(analysis_result, "Unsupported file type. Please upload a PNG, JPG, JPEG, or WEBP image.")

    def testing_upload_gemini(self):
        log_groClient = run_setup()
        logger=log_groClient[0]
        groq_client=log_groClient[1]
        self.assertEqual(upload_to_gemini('image_doesnt_exist.png', logger), None)
        pass

if __name__ == "__main__":
    unittest.main()