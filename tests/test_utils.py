import pytest
from flashlearn.utils import to_bool


class TestUtils:

	def test_to_boolean(self):
		assert to_bool("0") is False, "Should return False"
		assert to_bool("1") is True, "Should return True"
		assert to_bool("true") is True, "Should return True"
		assert to_bool("false") is False, "Should return False"
		assert to_bool(True) is True, "Should return True"
		assert to_bool(False) is False, "Should return False"

		with pytest.raises(ValueError):
			to_bool("a shrubbery!")
