from django.test import TestCase
from django.core.files.base import ContentFile
from django.utils.six import BytesIO
from django.conf import settings

from PIL import Image

from whalesdb import models

import os


class TestMorMooringSetup(TestCase):

    def setUp(self) -> None:
        pass

    def test_create_mor(self):

        img_file_name = "MooringSetupTest.png"
        img_file_path = os.path.dirname(os.path.realpath(__file__)) + os.path.sep + "data" + os.path.sep + img_file_name

        data = BytesIO()
        Image.open(img_file_path).save(data, "PNG")
        data.seek(0)
        file = ContentFile(data.read(), img_file_name)

        self.mooring_dic = {}

        mor_1 = models.MorMooringSetup(mor_name="MOR001", mor_max_depth=100,
                                       mor_link_setup_image="https://somelink.com", mor_setup_image=file)
        mor_1.save()

        # Check that the file was saved
        expected_path = os.path.join(settings.MEDIA_DIR, "whalesdb", "mooring_setup", img_file_name)
        self.assertTrue(os.path.exists(expected_path))
        self.assertTrue(os.path.isfile(expected_path))

        # Delete the image
        mor_1.delete()

        self.assertFalse(os.path.exists(expected_path))
