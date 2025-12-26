# stdlib
import pathlib

# this package
import dom_toml


def test_dump(tmp_path: pathlib.Path):
	toml_obj = {"testing": "test\ntest"}
	path = tmp_path / "test.toml"
	dom_toml.dump(toml_obj, path)
	assert path.read_bytes().decode() == 'testing = "test\\ntest"\n'
