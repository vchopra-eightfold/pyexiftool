# -*- coding: utf-8 -*-
"""
Test :: ExifToolHelper - set_tags tests
"""

# standard
import unittest
import shutil

# test helpers
from tests.common_util import et_get_temp_dir, TEST_IMAGE_DIR, TEST_IMAGE_JPG

# custom
import exiftool
from exiftool.exceptions import ExifToolExecuteError



class TestHelperSetTags(unittest.TestCase):

	# ---------------------------------------------------------------------------------------------------------
	def setUp(self):
		self.et = exiftool.ExifToolHelper(
			common_args=["-G", "-n", "-overwrite_original"],
			encoding="UTF-8"
		)

	def tearDown(self):
		self.et.terminate()


	# ---------------------------------------------------------------------------------------------------------
	def test_set_tags(self):
		(temp_obj, temp_dir) = et_get_temp_dir(suffix="settag")

		mod_prefix = "newcap_"
		expected_data = [
			{
				"SourceFile": "rose.jpg",
				"Caption-Abstract": "Ein Röschen ganz allein",
			},
			{
				"SourceFile": "skyblue.png",
				"Caption-Abstract": "Blauer Himmel"
			},
		]
		source_files = []

		for d in expected_data:
			d["SourceFile"] = f = TEST_IMAGE_DIR / d["SourceFile"]
			self.assertTrue(f.exists())

			f_mod = temp_dir / (mod_prefix + f.name)

			self.assertFalse(
				f_mod.exists(),
				f"{f_mod} should not exist before the test. Please delete.",
			)

			shutil.copyfile(f, f_mod)
			source_files.append(f_mod)
			with self.et:
				self.et.set_tags([f_mod], {"Caption-Abstract": d["Caption-Abstract"]})
				result = self.et.get_tags([f_mod], "IPTC:Caption-Abstract")[0]
				tag0 = list(result.values())[1]
			#f_mod.unlink()  # don't delete file, tempdir will take care of it
			self.assertEqual(tag0, d["Caption-Abstract"])


	# ---------------------------------------------------------------------------------------------------------
	def test_set_tags_file_existence(self):
		""" test setting tags on a non-existent file """
		(temp_obj, temp_dir) = et_get_temp_dir(suffix="settagfe")

		self.assertTrue(self.et.check_execute)

		junk_tag = {"not_a_valid_tag_foo_bar": "lorem ipsum"}

		# set up temp working file
		mod_prefix = "test_"
		f = TEST_IMAGE_DIR / "rose.jpg"
		f_mod = temp_dir / (mod_prefix + f.name)
		self.assertTrue(f.exists())
		self.assertFalse(f_mod.exists())
		shutil.copyfile(f, f_mod)


		self.et.check_execute = False

		# no errors (aka exiftool fails silently, even though file doesn't exist)
		self.et.set_tags("foo.bar", junk_tag)

		# no errors (aka exiftool fails silently, even though it can't set this tag)
		self.et.set_tags(f_mod, junk_tag)



		self.et.check_execute = True

		# proper error handling, should raise error
		with self.assertRaises(ExifToolExecuteError):
			self.et.set_tags("foo.bar", junk_tag)


		# proper error handling, should also raise error
		with self.assertRaises(ExifToolExecuteError):
			self.et.set_tags(f_mod, junk_tag)


	# ---------------------------------------------------------------------------------------------------------
	def test_set_tags_files_invalid(self):
		""" test to cover the files == None """

		with self.assertRaises(ValueError):
			self.et.set_tags(None, [])


	# ---------------------------------------------------------------------------------------------------------
	def test_set_tags_tags_invalid(self):
		""" test to cover the files == None """

		with self.assertRaises(ValueError):
			self.et.set_tags("rose.jpg", None)


		with self.assertRaises(TypeError):
			self.et.set_tags("rose.jpg", object())


	# ---------------------------------------------------------------------------------------------------------
	def test_set_tags_list_keywords(self):
		"""
		test that covers setting keywords in set_tags() using a list (not using the ExifToolAlpha's keywords functionality directly)
		"""
		(temp_obj, temp_dir) = et_get_temp_dir(suffix="settagkw")

		mod_prefix = "newkw_"
		expected_data = [{"SourceFile": "rose.jpg",
						  "Keywords": ["nature", "red plant", "flower"]}]
		source_files = []

		for d in expected_data:
			d["SourceFile"] = f = TEST_IMAGE_DIR / d["SourceFile"]
			self.assertTrue(f.exists())
			f_mod = temp_dir / (mod_prefix + f.name)
			self.assertFalse(
				f_mod.exists(),
				f"{f_mod} should not exist before the test. Please delete.",
			)

			shutil.copyfile(f, f_mod)
			source_files.append(f_mod)

			with self.et:
				self.et.set_tags(f_mod, {"Keywords": expected_data[0]["Keywords"]})
				ret_data = self.et.get_tags(f_mod, "IPTC:Keywords")

			#f_mod.unlink()  # don't delete file, tempdir will take care of it

			self.assertEqual(ret_data[0]["IPTC:Keywords"], expected_data[0]["Keywords"])

	# ---------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
	unittest.main()