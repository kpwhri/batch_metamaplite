from textwrap import dedent

import pytest

from mml_utils.scripts.extract_mml_output import extract_mml_from_mmi_data, extract_mmi_line


def fix_text(text):
    return ''.join(dedent(text).split('\n'))


@pytest.fixture()
def mmi_risk_of():
    return fix_text(
        '''00000000.tx|MMI|27.63|Risk|C0035647|[idcn]|"risk of"-text-0-"risk of"--0,"risk of"-text-0-"risk of"--0,
        "risk of"-text-20-"risk of"--0|text|2672/7;3076/7;4271/7|G17.680.750;N06.850.520.830.600.800;N05.715.360.
        750.625.700;E05.318.740.600.80'''
    )


def get_mmi_lines(mmi_lines, exp):
    if isinstance(exp, str):
        exp = [exp]
    for line, expected in zip(mmi_lines.split('\n'), exp):
        yield line.split('|'), expected


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), '00000000.tx'),
])
def test_extract_mmi_filename(mmi_lines, exp):
    for line, expected in get_mmi_lines(mmi_lines, exp):
        res = extract_mmi_line(line)
        assert expected == res['docid']


def test_mmi_skips():
    line = '23074487|AA|FY|fiscal years|1|2|3|12|9362:2'.split('|')
    assert extract_mmi_line(line) is None


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'Risk'),
])
def test_extract_mmi_preferredname(mmi_lines, exp):
    for line, expected in get_mmi_lines(mmi_lines, exp):
        res = extract_mmi_line(line)
        assert expected == res['preferredname']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'C0035647'),
])
def test_extract_mmi_cui(mmi_lines, exp):
    for line, expected in get_mmi_lines(mmi_lines, exp):
        res = extract_mmi_line(line)
        assert expected == res['cui']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'idcn'),
])
def test_extract_mmi_semantictype(mmi_lines, exp):
    for line, expected in get_mmi_lines(mmi_lines, exp):
        res = extract_mmi_line(line)
        assert expected == res['semantictype']
        assert res[expected] == 1
