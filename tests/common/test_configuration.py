# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
from os import environ, mkdir
from os.path import join
from tempfile import TemporaryDirectory

import pytest

from conda.auxlib.ish import dals
from conda.common.compat import odict
from conda.common.configuration import (
    Configuration,
    ConfigurationObject,
    ObjectParameter,
    ParameterFlag,
    ParameterLoader,
    PrimitiveParameter,
    MapParameter,
    SequenceParameter,
    YamlRawParameter,
    load_file_configs,
    InvalidTypeError,
    CustomValidationError,
    ValidationError,
)
from conda.common.io import env_var, env_vars
from conda.common.serialize import yaml_round_trip_load

_TEST_YAML_RAW = {
    "file1": dals(
        """
        always_yes: no

        proxy_servers:
          http: taz
          https: sly
          s3: pepé

        channels_altname:
          - bugs
          - daffy
          - tweety
        """
    ),
    "file2": dals(
        """
        always_yes: yes
        changeps1: no

        proxy_servers:
          http: marv
          https: sam

        channels:
          - porky
          - bugs
          - elmer
        """
    ),
    "file3": dals(
        """
        always_yes_altname2: yes  #!final

        proxy_servers:
          http: foghorn  #!final
          https: elmer
          s3: porky

        channels:
          - wile   #!top
          - daffy
          - foghorn
        """
    ),
    "file4": dals(
        """
        always_yes: yes  #!final
        changeps1: no  #!final

        proxy_servers:  #!final
          http: bugs
          https: daffy

        channels:  #!final
          - pepé
          - marv
          - sam
        """
    ),
    "file5": dals(
        """
        channels:
          - pepé
          - marv   #!top
          - sam
        """
    ),
    "file6": dals(
        """
        channels:
          - elmer
          - marv  #!bottom
          - bugs
        """
    ),
    "file7": dals(
        """
        channels:
          - wile
          - daffy  #!top
          - sam    #!top
          - foghorn
        """
    ),
    "file8": dals(
        """
        channels:
          - pepé  #!bottom
          - marv  #!top
          - wile
          - sam
        """
    ),
    "file9": dals(
        """
        channels: #!final
          - sam
          - pepé
          - marv   #!top
          - daffy  #!bottom
        """
    ),
    "bad_boolean": "always_yes: yeah",
    "too_many_aliases": dals(
        """
        always_yes: yes
        always_yes_altname2: yes
        """
    ),
    "not_an_int": "always_an_int: nope",
    "good_boolean_map": dals(
        """
        boolean_map:
          a_true: true
          a_yes: yes
          a_1: 1
          a_false: False
          a_no: no
          a_0: 0
        """
    ),
    "bad_boolean_map": dals(
        """
        boolean_map:
          a_string: not true
          an_int: 2
          a_float: 1.2
          a_complex: 1+2j
        proxy_servers:
        channels:
        """
    ),
    "commented_map": dals(
        """
        commented_map:
          key:
            # comment
            value
        """
    ),
    "env_var_map": dals(
        """
        env_var_map:
          expanded: $EXPANDED_VAR
          unexpanded: $UNEXPANDED_VAR

        env_var_str: $EXPANDED_VAR
        env_var_bool: $BOOL_VAR
        normal_str: $EXPANDED_VAR

        env_var_list:
          - $EXPANDED_VAR
          - $UNEXPANDED_VAR
          - regular_var
        """
    ),
    "nestedFile1": dals(
        """
        nested_map:
            key1:
                - a1
                - b1 #!bottom
                - c1
            key2:
                - d1
                - e1
                - f1
        nested_seq:
            - #!bottom
                key1: a1
                key2: b1
            - #!top
                key3: c1
                key4: d1
        """
    ),
    "nestedFile2": dals(
        """
        nested_map:
            key1:
                - a2
                - b2
                - c2
                - d2 #!top
            key2: #!final
                - d2
                - e2
                - f2
        nested_seq:
            -
                key1: a2
                key2: b2
            -
                key3: c2
                key4: d2
        """
    ),
    "objectFile1": dals(
        """
        test_object:
            int_field: 10
            str_field: sample
            map_field:
                key1: a1
                key2: b1
            seq_field:
                - a1
                - b1
                - c1
        """
    ),
    "objectFile2": dals(
        """
        test_object:
            int_field: 10
            str_field: override
            map_field:
                key2: b2
                key3: c2
            seq_field:
                - a2
                - b2
        """
    ),
    "bad_proxy": "proxy_servers: bad values",
}


def _generate_fixture(name, config):
    @pytest.fixture(scope="session")
    def fixture():
        return YamlRawParameter.make_raw_parameters(name, yaml_round_trip_load(config))

    return fixture


def _generate_fixtures():
    global _TEST_YAML_RAW
    global _generate_fixture
    global _generate_fixtures

    for name, config in _TEST_YAML_RAW.items():
        globals()[name.upper()] = config
        globals()[name] = _generate_fixture(name, config)

    del _generate_fixtures
    del _generate_fixture
    del _TEST_YAML_RAW


_generate_fixtures()


class DummyTestObject(ConfigurationObject):
    def __init__(self):
        self.int_field = PrimitiveParameter(0, element_type=int)
        self.str_field = PrimitiveParameter("", element_type=str)
        self.map_field = MapParameter(PrimitiveParameter("", element_type=str))
        self.seq_field = SequenceParameter(PrimitiveParameter("", element_type=str))


class SampleConfiguration(Configuration):
    always_yes = ParameterLoader(PrimitiveParameter(False),
                                 aliases=('always_yes_altname1', 'yes', 'always_yes_altname2'))
    changeps1 = ParameterLoader(PrimitiveParameter(True))
    proxy_servers = ParameterLoader(MapParameter(PrimitiveParameter("", element_type=str)))
    channels = ParameterLoader(SequenceParameter(PrimitiveParameter("", element_type=str)),
                               aliases=('channels_altname',))

    always_an_int = ParameterLoader(PrimitiveParameter(0))
    boolean_map = ParameterLoader(MapParameter(PrimitiveParameter(False, element_type=bool)))
    commented_map = ParameterLoader(MapParameter(PrimitiveParameter("", str)))

    env_var_map = ParameterLoader(
        MapParameter(PrimitiveParameter("", str)),
        expandvars=True)
    env_var_str = ParameterLoader(PrimitiveParameter(''), expandvars=True)
    env_var_bool = ParameterLoader(PrimitiveParameter(False, element_type=bool), expandvars=True)
    normal_str = ParameterLoader(PrimitiveParameter(''), expandvars=False)
    env_var_list = ParameterLoader(
        SequenceParameter(PrimitiveParameter('', str)),
        expandvars=True)

    nested_map = ParameterLoader(
        MapParameter(SequenceParameter(PrimitiveParameter("", element_type=str))))
    nested_seq = ParameterLoader(
        SequenceParameter(MapParameter(PrimitiveParameter("", element_type=str))))

    test_object = ParameterLoader(
        ObjectParameter(DummyTestObject()))


def test_simple_merges_and_caching(file1, file2):
    raw_data = {"file1": file1, "file2": file2}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.channels == ("porky", "bugs", "elmer", "daffy", "tweety")
    assert config.proxy_servers == {"http": "marv", "https": "sam", "s3": "pepé"}

    raw_data = {"file2": file2, "file1": file1}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert len(config._cache_) == 0
    assert config.changeps1 is False
    assert len(config._cache_) == 1
    assert config.always_yes is False
    assert len(config._cache_) == 2
    assert config.always_yes is False
    assert config._cache_["always_yes"] is False
    assert config.channels == ("bugs", "daffy", "tweety", "porky", "elmer")
    assert config.proxy_servers == {"http": "taz", "https": "sly", "s3": "pepé"}


def test_default_values():
    config = SampleConfiguration()
    assert config.channels == ()
    assert config.always_yes is False
    assert config.proxy_servers == {}
    assert config.changeps1 is True


def test_env_var_config():
    def make_key(appname, key):
        return f"{appname.upper()}_{key.upper()}"

    appname = "myapp"
    test_dict = {}
    test_dict[make_key(appname, "always_yes")] = "yes"
    test_dict[make_key(appname, "changeps1")] = "false"

    try:
        environ.update(test_dict)
        assert "MYAPP_ALWAYS_YES" in environ
        config = SampleConfiguration(app_name=appname)
        assert config.changeps1 is False
        assert config.always_yes is True
    finally:
        [environ.pop(key) for key in test_dict]


def test_env_var_config_alias():
    def make_key(appname, key):
        return f"{appname.upper()}_{key.upper()}"

    appname = "myapp"
    test_dict = {}
    test_dict[make_key(appname, "yes")] = "yes"
    test_dict[make_key(appname, "changeps1")] = "false"

    try:
        environ.update(test_dict)
        assert "MYAPP_YES" in environ
        config = SampleConfiguration()._set_env_vars(appname)
        assert config.always_yes is True
        assert config.changeps1 is False
    finally:
        [environ.pop(key) for key in test_dict]


def test_env_var_config_split_sequence():
    def make_key(appname, key):
        return f"{appname.upper()}_{key.upper()}"

    appname = "myapp"
    test_dict = {}
    test_dict[make_key(appname, "channels")] = "channel1,channel2"

    try:
        environ.update(test_dict)
        assert "MYAPP_CHANNELS" in environ
        config = SampleConfiguration()._set_env_vars(appname)
        assert config.channels == ("channel1", "channel2")
    finally:
        [environ.pop(key) for key in test_dict]


def test_env_var_config_no_split_sequence():
    def make_key(appname, key):
        return f"{appname.upper()}_{key.upper()}"

    appname = "myapp"
    test_dict = {}
    test_dict[make_key(appname, "channels")] = "channel1"

    try:
        environ.update(test_dict)
        assert "MYAPP_CHANNELS" in environ
        config = SampleConfiguration()._set_env_vars(appname)
        assert config.channels == ("channel1",)
    finally:
        [environ.pop(key) for key in test_dict]


def test_env_var_config_empty_sequence():
    def make_key(appname, key):
        return f"{appname.upper()}_{key.upper()}"

    appname = "myapp"
    test_dict = {}
    test_dict[make_key(appname, "channels")] = ""

    try:
        environ.update(test_dict)
        assert "MYAPP_CHANNELS" in environ
        config = SampleConfiguration()._set_env_vars(appname)
        assert config.channels == ()
    finally:
        [environ.pop(key) for key in test_dict]


def test_load_raw_configs():
    with TemporaryDirectory() as tempdir:
        condarc = join(tempdir, ".condarc")
        condarcd = join(tempdir, "condarc.d")
        f1 = join(condarcd, "file1.yml")
        f2 = join(condarcd, "file2.yml")
        not_a_file = join(tempdir, "not_a_file")

        mkdir(condarcd)

        with open(f1, "wb") as fh1, open(f2, "wb") as fh2, open(condarc, "wb") as fhrc:
            fh1.write(FILE1.encode("utf-8"))
            fh2.write(FILE2.encode("utf-8"))
            fhrc.write(FILE3.encode("utf-8"))
        search_path = [condarc, not_a_file, condarcd]
        raw_data = load_file_configs(search_path)
        assert not_a_file not in raw_data
        assert raw_data[condarc]["channels"].value(None)[0].value(None) == "wile"
        assert raw_data[f1]["always_yes"].value(None) == "no"
        assert raw_data[f2]["proxy_servers"].value(None)["http"].value(None) == "marv"

        config = SampleConfiguration(search_path)

        from pprint import pprint

        for key, val in config.collect_all().items():
            print(key)
            pprint(val)
        assert config.channels == ("wile", "porky", "bugs", "elmer", "daffy", "tweety", "foghorn")


def test_important_primitive_map_merges(file1, file2, file3, file4):
    raw_data = {"file1": file1, "file3": file3, "file2": file2}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.channels == ("wile", "porky", "bugs", "elmer", "daffy", "foghorn", "tweety")
    assert config.proxy_servers == {"http": "foghorn", "https": "sam", "s3": "porky"}

    raw_data = {"file3": file3, "file2": file2, "file1": file1}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.channels == ("wile", "bugs", "daffy", "tweety", "porky", "elmer", "foghorn")
    assert config.proxy_servers == {"http": "foghorn", "https": "sly", "s3": "pepé"}

    raw_data = {"file4": file4, "file3": file3, "file1": file1}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.proxy_servers == {"https": "daffy", "http": "bugs"}

    raw_data = {"file1": file1, "file4": file4, "file3": file3, "file2": file2}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.proxy_servers == {"http": "bugs", "https": "daffy", "s3": "pepé"}

    raw_data = {"file1": file1, "file2": file2, "file3": file3, "file4": file4}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.proxy_servers == {"https": "daffy", "http": "foghorn", "s3": "porky"}

    raw_data = {"file3": file3, "file1": file1}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is True
    assert config.always_yes is True
    assert config.proxy_servers == {"https": "sly", "http": "foghorn", "s3": "pepé"}

    raw_data = {"file4": file4, "file3": file3}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.changeps1 is False
    assert config.always_yes is True
    assert config.proxy_servers == {"http": "bugs", "https": "daffy"}


def test_list_merges(file3, file4, file5, file6, file7, file8, file9):
    raw_data = {"file5": file5, "file3": file3}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("marv", "wile", "daffy", "foghorn", "pepé", "sam")

    raw_data = {"file6": file6, "file5": file5, "file4": file4, "file3": file3}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("pepé", "sam", "elmer", "bugs", "marv")

    raw_data = {"file3": file3, "file4": file4, "file5": file5, "file6": file6}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("wile", "pepé", "marv", "sam", "daffy", "foghorn")

    raw_data = {"file6": file6, "file3": file3, "file4": file4, "file5": file5}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("wile", "pepé", "sam", "daffy", "foghorn", "elmer", "bugs", "marv")

    raw_data = {"file7": file7, "file8": file8, "file9": file9}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("sam", "marv", "wile", "foghorn", "daffy", "pepé")

    raw_data = {"file7": file7, "file9": file9, "file8": file8}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("sam", "marv", "pepé", "wile", "foghorn", "daffy")

    raw_data = {"file8": file8, "file7": file7, "file9": file9}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("marv", "sam", "wile", "foghorn", "daffy", "pepé")

    raw_data = {"file8": file8, "file9": file9, "file7": file7}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("marv", "sam", "wile", "daffy", "pepé")

    raw_data = {"file9": file9, "file7": file7, "file8": file8}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("marv", "sam", "pepé", "daffy")

    raw_data = {"file9": file9, "file8": file8, "file7": file7}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.channels == ("marv", "sam", "pepé", "daffy")


def test_validation(bad_boolean, too_many_aliases, not_an_int, bad_boolean_map, good_boolean_map):
    raw_data = {"bad_boolean": bad_boolean}
    config = SampleConfiguration()._set_raw_data(raw_data)
    with pytest.raises(ValidationError):
        config.always_yes

    raw_data = {"too_many_aliases": too_many_aliases}
    config = SampleConfiguration()._set_raw_data(raw_data)
    with pytest.raises(ValidationError):
        config.always_yes

    raw_data = {"not_an_int": not_an_int}
    config = SampleConfiguration()._set_raw_data(raw_data)
    with pytest.raises(ValidationError):
        config.always_an_int

    raw_data = {"bad_boolean_map": bad_boolean_map}
    config = SampleConfiguration()._set_raw_data(raw_data)
    with pytest.raises(ValidationError):
        config.boolean_map

    raw_data = {"good_boolean_map": good_boolean_map}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.boolean_map["a_true"] is True
    assert config.boolean_map["a_yes"] is True
    assert config.boolean_map["a_1"] is True
    assert config.boolean_map["a_false"] is False
    assert config.boolean_map["a_no"] is False
    assert config.boolean_map["a_0"] is False


def test_parameter():
    assert ParameterFlag.from_name("top") is ParameterFlag.top


def test_validate_all(file1, bad_boolean_map):
    raw_data = {"file1": file1}
    config = SampleConfiguration()._set_raw_data(raw_data)
    config.validate_configuration()

    raw_data = {"bad_boolean_map": bad_boolean_map}
    config = SampleConfiguration()._set_raw_data(raw_data)
    # the `proxy_servers: ~` part of 'bad_boolean_map' is a regression test for #4757
    # in the future, CustomValidationError should probably be a MultiValidationError
    # with TypeValidationError for 'proxy_servers' and 'channels'
    with pytest.raises(CustomValidationError):
        config.validate_configuration()


def test_cross_parameter_validation():
    pass
    # test primitive can't be list; list can't be map, etc


def test_map_parameter_must_be_map(bad_proxy):
    # regression test for conda/conda#3467
    raw_data = {"bad_proxy": bad_proxy}
    config = SampleConfiguration()._set_raw_data(raw_data)
    with pytest.raises(InvalidTypeError):
        config.validate_all()


def test_config_resets():
    appname = "myapp"
    config = SampleConfiguration(app_name=appname)
    assert config.changeps1 is True
    with env_var("MYAPP_CHANGEPS1", "false"):
        config.__init__(app_name=appname)
        assert config.changeps1 is False


def test_empty_map_parameter(bad_boolean_map):
    raw_data = {"bad_boolean_map": bad_boolean_map}
    config = SampleConfiguration()._set_raw_data(raw_data)
    config.check_source("bad_boolean_map")


def test_commented_map_parameter(commented_map):
    raw_data = {"commented_map": commented_map}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.commented_map == {"key": "value"}


def test_invalid_map_parameter():
    data = odict(s1=YamlRawParameter.make_raw_parameters("s1", {"proxy_servers": "blah"}))
    config = SampleConfiguration()._set_raw_data(data)
    with pytest.raises(InvalidTypeError):
        config.proxy_servers


def test_invalid_seq_parameter():
    data = odict(s1=YamlRawParameter.make_raw_parameters("s1", {"channels": "y_u_no_tuple"}))
    config = SampleConfiguration()._set_raw_data(data)
    with pytest.raises(InvalidTypeError):
        config.channels


def test_expanded_variables(env_var_map):
    with env_vars({"EXPANDED_VAR": "itsexpanded", "BOOL_VAR": "True"}):
        raw_data = {"env_var_map": env_var_map}
        config = SampleConfiguration()._set_raw_data(raw_data)
        assert config.env_var_map["expanded"] == "itsexpanded"
        assert config.env_var_map["unexpanded"] == "$UNEXPANDED_VAR"
        assert config.env_var_str == "itsexpanded"
        assert config.env_var_bool is True
        assert config.normal_str == "$EXPANDED_VAR"
        assert config.env_var_list == ("itsexpanded", "$UNEXPANDED_VAR", "regular_var")


def test_nested(nestedFile1, nestedFile2):
    raw_data = {"nestedFile1": nestedFile1, "nestedFile2": nestedFile2}
    config = SampleConfiguration()._set_raw_data(raw_data)
    assert config.nested_seq == (
        {"key3": "c1", "key4": "d1"},  # top item from nestedFile1
        {"key1": "a2", "key2": "b2"},
        {"key3": "c2", "key4": "d2"},
        {"key1": "a1", "key2": "b1"},
    )  # bottom item from nestedFile2
    assert config.nested_map == {
        "key1": ("d2", "a2", "b2", "c2", "a1", "c1", "b1"),
        "key2": ("d2", "e2", "f2"),
    }


def test_object(objectFile1, objectFile2):
    raw_data = {"objectFile1": objectFile1, "objectFile2": objectFile2}
    config = SampleConfiguration()._set_raw_data(raw_data)
    test_object = config.test_object
    assert test_object.int_field == 10
    assert test_object.str_field == "override"
    assert test_object.map_field == {"key1": "a1", "key2": "b2", "key3": "c2"}
    assert test_object.seq_field == ("a2", "b2", "a1", "b1", "c1")
