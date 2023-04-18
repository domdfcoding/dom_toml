# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

# this package
import dom_toml


class TestDump:
	expected = 'hello = "world"\n'
	match = "Passing encoder=None to 'dom_toml.dumps' is deprecated since 0.5.0 and support will be removed in 1.0.0"

	def test_dumps_encoder_none(self):

		with pytest.warns(DeprecationWarning, match=self.match):
			assert dom_toml.dumps({"hello": "world"}, encoder=None) == self.expected  # type: ignore[arg-type]

	def test_dump_encoder_none(self, tmp_pathplus: PathPlus):

		with pytest.warns(DeprecationWarning, match=self.match):
			dom_toml.dump(
					{"hello": "world"},
					filename=tmp_pathplus / "config.toml",
					encoder=None,  # type: ignore[arg-type]
					)

		assert (tmp_pathplus / "config.toml").read_text() == self.expected
