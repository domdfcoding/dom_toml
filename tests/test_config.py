# stdlib
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Type, Union, no_type_check

# 3rd party
import attrs
import pytest
from coincidence.regressions import AdvancedDataRegressionFixture, AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus

# this package
from dom_toml.config import Config, subtable_field, table_name, to_kebab_case
from dom_toml.config.fields import Boolean, Integer, Number, String


@table_name("savitzky-golay")
@attrs.define
class SavitzkyGolayMethod(Config):

	enable: bool = Boolean.field(default=True)
	window: int = attrs.field(default=7)
	degree: int = Integer.field(default=2)


def _convert_sg_method(method: Union[bool, "SavitzkyGolayMethod", Dict[str, Any]]) -> "SavitzkyGolayMethod":
	if isinstance(method, bool):
		return SavitzkyGolayMethod()
	elif isinstance(method, SavitzkyGolayMethod):
		return method
	else:
		return SavitzkyGolayMethod(**method)


@attrs.define
class IntensityMatrixMethod(Config):

	crop_mass_range: Optional[Tuple[int, int]] = attrs.field(default=(50, 500))

	savitzky_golay: SavitzkyGolayMethod = attrs.field(
			default=SavitzkyGolayMethod(),
			converter=_convert_sg_method,
			)

	tophat: bool = Boolean.field(default=True)
	tophat_structure_size: str = String.field(default="1.5m")


@attrs.define
class PeakDetectionMethod(Config):

	points: int = Integer.field(default=10)
	scans: int = Integer.field(default=1)


def default_base_peak_filter() -> Sequence[int]:
	"""
	Returns the default value for the ``base_peak_filter`` option.
	"""

	return (73, 147)


@attrs.define
class PeakFilterMethod(Config):

	noise_filter: bool = Boolean.field(default=True)
	noise_threshold: int = Integer.field(default=2)

	base_peak_filter: Set[int] = attrs.field(
			default=attrs.Factory(default_base_peak_filter),
			converter=tuple,
			)


@attrs.define
class AlignmentMethod(Config):

	rt_modulation: float = Number.field(default=2.5)
	gap_penalty: float = Number.field(default=0.3)
	min_peaks: int = Integer.field(default=1)
	top_n_peaks: int = Integer.field(default=80)
	min_peak_area: float = Number.field(default=0.0)


@attrs.define
class ConsolidateMethod(Config):

	name_filter: List[str] = attrs.field(converter=list, default=attrs.Factory(list))
	min_match_factor: int = Integer.field(default=600)
	min_appearances: int = Integer.field(default=-1)


@attrs.define
class Method(Config):
	"""
	Overall GunShotMatch method.
	"""

	#: Method used for constructing an intensity matrix from a datafile.
	intensity_matrix: IntensityMatrixMethod = subtable_field(IntensityMatrixMethod)

	#: Method used for Biller-Biemann peak detection.
	peak_detection: PeakDetectionMethod = subtable_field(PeakDetectionMethod)

	#: Method used for peak filtering.
	peak_filter: PeakFilterMethod = subtable_field(PeakFilterMethod)

	#: Method used for peak alignment.
	alignment: AlignmentMethod = subtable_field(AlignmentMethod)

	#: Method used for consolidation (finding most likely identity for aligned peaks).
	consolidate: ConsolidateMethod = subtable_field(ConsolidateMethod)


@pytest.mark.parametrize(
		"cls",
		[
				pytest.param(AlignmentMethod, id="AlignmentMethod"),
				pytest.param(PeakFilterMethod, id="PeakFilterMethod"),
				pytest.param(ConsolidateMethod, id="ConsolidateMethod"),
				pytest.param(PeakDetectionMethod, id="PeakDetectionMethod"),
				pytest.param(SavitzkyGolayMethod, id="SavitzkyGolayMethod"),
				pytest.param(IntensityMatrixMethod, id="IntensityMatrixMethod"),
				pytest.param(Method, id="Method"),
				],
		)
def test_default_methods(advanced_data_regression: AdvancedDataRegressionFixture, cls: Type[Config]):
	method = cls()
	advanced_data_regression.check(method.to_dict())


@pytest.mark.parametrize(
		"cls",
		[
				pytest.param(AlignmentMethod, id="AlignmentMethod"),
				pytest.param(PeakFilterMethod, id="PeakFilterMethod"),
				pytest.param(ConsolidateMethod, id="ConsolidateMethod"),
				pytest.param(PeakDetectionMethod, id="PeakDetectionMethod"),
				pytest.param(SavitzkyGolayMethod, id="SavitzkyGolayMethod"),
				pytest.param(IntensityMatrixMethod, id="IntensityMatrixMethod"),
				pytest.param(Method, id="Method"),
				],
		)
def test_to_toml(advanced_file_regression: AdvancedFileRegressionFixture, cls: Type[Config]):
	method = cls()
	advanced_file_regression.check(method.to_toml())


@pytest.mark.parametrize(
		"cls, kwargs",
		[
				pytest.param(SavitzkyGolayMethod, {"enable": False}, id="savgol_false"),
				pytest.param(SavitzkyGolayMethod, {"window": 8}, id="savgol_window"),
				pytest.param(SavitzkyGolayMethod, {"window": "1m"}, id="savgol_window_str_min"),
				pytest.param(SavitzkyGolayMethod, {"window": "20s"}, id="savgol_window_str_sec"),
				pytest.param(SavitzkyGolayMethod, {"degree": 5}, id="savgol_degree"),
				pytest.param(SavitzkyGolayMethod, {"window": 8, "degree": 5}, id="savgol_window_degree"),
				pytest.param(IntensityMatrixMethod, {"crop_mass_range": [100, 200]}, id="im_mass_range"),
				pytest.param(
						IntensityMatrixMethod,
						{"tophat_structure_size": "2m"},
						id="im_tophat_structure_size",
						),
				pytest.param(
						IntensityMatrixMethod,
						{"savitzky_golay": {"enable": False}},
						id="im_savgol_dict_false",
						),
				pytest.param(
						IntensityMatrixMethod,
						{"savitzky_golay": {"window": 10}},
						id="im_savgol_dict_window",
						),
				pytest.param(IntensityMatrixMethod, {"savitzky_golay": False}, id="im_savgol_false"),
				pytest.param(PeakDetectionMethod, {"points": 8}, id="peak_detection_points"),
				pytest.param(PeakDetectionMethod, {"scans": 3}, id="peak_detection_scans"),
				pytest.param(PeakFilterMethod, {"noise_filter": False}, id="peak_filter_noise_filter"),
				pytest.param(PeakFilterMethod, {"noise_threshold": 5}, id="peak_filter_noise_threshold"),
				pytest.param(
						PeakFilterMethod,
						{"base_peak_filter": [1, 2, 3, 4, 5]},
						id="peak_filter_base_peak_filter_list",
						),
				pytest.param(
						PeakFilterMethod,
						{"base_peak_filter": {1, 2, 3, 4, 5}},
						id="peak_filter_base_peak_filter_set",
						),
				pytest.param(AlignmentMethod, {"rt_modulation": 10}, id="alignment_rt_modulation"),
				pytest.param(AlignmentMethod, {"gap_penalty": 0.2}, id="alignment_gap_penalty"),
				pytest.param(AlignmentMethod, {"min_peaks": 5}, id="alignment_min_peaks"),
				pytest.param(AlignmentMethod, {"top_n_peaks": 50}, id="alignment_top_n_peaks"),
				pytest.param(AlignmentMethod, {"min_peak_area": 1.5e6}, id="alignment_min_peak_area"),
				],
		)
def test_partial_arguments(
		advanced_data_regression: AdvancedDataRegressionFixture,
		cls: Type[Config],
		kwargs: Dict[str, Any],
		):
	method = cls(**kwargs)
	advanced_data_regression.check(method.to_dict())

	method = cls.from_dict(kwargs)
	advanced_data_regression.check(method.to_dict())


def test_from_toml(advanced_data_regression: AdvancedDataRegressionFixture):
	config_file = PathPlus(__file__).parent / "method.toml"
	config_toml = config_file.read_text()

	method = Method.from_toml(config_toml)
	advanced_data_regression.check(method.to_dict())


def test_from_json(advanced_data_regression: AdvancedDataRegressionFixture):
	config_file = PathPlus(__file__).parent / "method.json"
	config_json = config_file.read_text()

	method = Method.from_json(config_json)
	advanced_data_regression.check(method.to_dict())


def test_coerce_error():
	with pytest.raises(TypeError, match="Cannot convert str to a PeakFilterMethod"):
		Method(peak_filter="banana")  # type: ignore[arg-type]

	with pytest.raises(TypeError, match="Cannot convert str to an IntensityMatrixMethod"):
		Method(intensity_matrix="banana")  # type: ignore[arg-type]


@attrs.define
class FieldsMethod(Config):

	boolean_field: bool = Boolean.field(default=True)
	integer_field: int = Integer.field(default=2)
	number_field: float = Number.field(default=2.0)
	string_field: float = String.field(default="abcdefg")


@attrs.define
class FieldsMethodNew(Config):

	boolean_field: bool = Boolean(default=True)  # type: ignore[assignment]
	integer_field: int = Integer(default=2)  # type: ignore[assignment]
	number_field: float = Number(default=2.0)  # type: ignore[assignment]
	string_field: float = String(default="abcdefg")  # type: ignore[assignment]


@no_type_check
@pytest.mark.parametrize("method", [FieldsMethod, FieldsMethodNew])
def test_fields(method: Type[Config]):
	method(boolean_field=1234)
	method(integer_field=1234)
	method(number_field=1234)
	method(string_field=1234)

	method(boolean_field=12.34)
	method(integer_field=12.34)
	method(number_field=12.34)
	method(string_field=12.34)

	method(boolean_field="abcdefg")

	with pytest.raises(ValueError, match=r"invalid literal for int\(\) with base 10: 'abcdefg'"):
		method(integer_field="abcdefg")

	with pytest.raises(ValueError, match=r"could not convert string to float: 'abcdefg'"):
		method(number_field="abcdefg")

	method(string_field="abcdefg")

	method(boolean_field=None)

	with pytest.raises(
			TypeError,
			match=r"int\(\) argument must be a string, a bytes-like object or a (real )?number, not 'NoneType'",
			):
		method(integer_field=None)

	with pytest.raises(
			TypeError,
			match=r"float\(\) argument must be a string or a (real )?number, not 'NoneType'",
			):
		method(number_field=None)

	method(string_field=None)

	method(boolean_field={"abcdefg": None})

	with pytest.raises(
			TypeError,
			match=r"int\(\) argument must be a string, a bytes-like object or a (real )?number, not 'dict'",
			):
		method(integer_field={"abcdefg": None})

	with pytest.raises(TypeError, match=r"float\(\) argument must be a string or a (real )?number, not 'dict'"):
		method(number_field={"abcdefg": None})

	method(string_field={"abcdefg": None})

	method().boolean_field = 1234
	method().integer_field = 1234
	method().number_field = 1234
	method().string_field = 1234

	method().boolean_field = 12.34
	method().integer_field = 12.34
	method().number_field = 12.34
	method().string_field = 12.34

	method().boolean_field = "abcdefg"

	with pytest.raises(ValueError, match=r"invalid literal for int\(\) with base 10: 'abcdefg'"):
		method().integer_field = "abcdefg"

	with pytest.raises(ValueError, match=r"could not convert string to float: 'abcdefg'"):
		method().number_field = "abcdefg"

	method().string_field = "abcdefg"

	method().boolean_field = None

	with pytest.raises(
			TypeError,
			match=r"int\(\) argument must be a string, a bytes-like object or a (real )?number, not 'NoneType'",
			):
		method().integer_field = None

	with pytest.raises(
			TypeError,
			match=r"float\(\) argument must be a string or a (real )?number, not 'NoneType'",
			):
		method().number_field = None

	method().string_field = None

	method().boolean_field = {"abcdefg": None}

	with pytest.raises(
			TypeError,
			match=r"int\(\) argument must be a string, a bytes-like object or a (real )?number, not 'dict'",
			):
		method().integer_field = {"abcdefg": None}

	with pytest.raises(TypeError, match=r"float\(\) argument must be a string or a (real )?number, not 'dict'"):
		method().number_field = {"abcdefg": None}

	method().string_field = {"abcdefg": None}


def test_kebab_case():
	assert to_kebab_case("FooBar") == "foo-bar"
	assert to_kebab_case("FooBBar") == "foo-b-bar"
	assert to_kebab_case("Foo_Bar") == "foo-bar"
	assert to_kebab_case("foo_bar") == "foo-bar"
	assert to_kebab_case("foobar") == "foobar"
	assert to_kebab_case("FooBar123") == "foo-bar123"

	assert to_kebab_case(Config) == "config"
	assert to_kebab_case(SavitzkyGolayMethod) == "savitzky-golay"
	assert to_kebab_case(IntensityMatrixMethod) == "intensity-matrix-method"
	assert to_kebab_case(PeakDetectionMethod) == "peak-detection-method"
	assert to_kebab_case(PeakFilterMethod) == "peak-filter-method"
	assert to_kebab_case(AlignmentMethod) == "alignment-method"
	assert to_kebab_case(ConsolidateMethod) == "consolidate-method"
	assert to_kebab_case(Method) == "method"
	assert to_kebab_case(FieldsMethod) == "fields-method"
	assert to_kebab_case(FieldsMethodNew) == "fields-method-new"

	assert to_kebab_case(Config()) == "config"
	assert to_kebab_case(SavitzkyGolayMethod()) == "savitzky-golay"
	assert to_kebab_case(IntensityMatrixMethod()) == "intensity-matrix-method"
	assert to_kebab_case(PeakDetectionMethod()) == "peak-detection-method"
	assert to_kebab_case(PeakFilterMethod()) == "peak-filter-method"
	assert to_kebab_case(AlignmentMethod()) == "alignment-method"
	assert to_kebab_case(ConsolidateMethod()) == "consolidate-method"
	assert to_kebab_case(Method()) == "method"
	assert to_kebab_case(FieldsMethod()) == "fields-method"
	assert to_kebab_case(FieldsMethodNew()) == "fields-method-new"
