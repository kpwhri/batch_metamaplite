import itertools
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
    if isinstance(exp, (str, int)):
        exp = [exp]
    for line in mmi_lines.split('\n'):
        for res, expected in zip(extract_mmi_line(line.split('|')), itertools.cycle(exp)):
            yield res, expected


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), '00000000.tx'),
])
def test_extract_mmi_filename(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['docid']


def test_mmi_skips():
    line = '23074487|AA|FY|fiscal years|1|2|3|12|9362:2'.split('|')
    assert len(list(extract_mmi_line(line))) == 0


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'Risk'),
])
def test_extract_mmi_conceptstring(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['conceptstring']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'C0035647'),
])
def test_extract_mmi_cui(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['cui']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 'idcn'),
])
def test_extract_mmi_semantictype(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['semantictype']
        assert res[expected] == 1


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), [0, 0, 0]),
])
def test_extract_mmi_negated(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['negated']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), [2672, 3076, 4271]),
])
def test_extract_mmi_start(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['start']


@pytest.mark.parametrize(('mmi_lines', 'exp'), [
    (pytest.lazy_fixture('mmi_risk_of'), 7),
])
def test_extract_mmi_length(mmi_lines, exp):
    for res, expected in get_mmi_lines(mmi_lines, exp):
        assert expected == res['length']


@pytest.mark.parametrize(('posinfo', 'exp'), [
    pytest.param(
        '[4061/10,4075/11],[4166/10,4180/11]', '?',
        marks=[
            pytest.mark.skip(
                reason='This is tough...and rare: https://lhncbc.nlm.nih.gov/ii/tools/MetaMap/Docs/MMI_Output_2016.pdf')
        ]
    ),
])
def test_positional_info(posinfo, exp):
    pass


def test_from_text(mmi_risk_of):
    res = list(extract_mml_from_mmi_data(mmi_risk_of, 'filename'))
    assert len(res) == 3
    assert {d['event_id'] for d in res} == {'filename_0', 'filename_1', 'filename_2'}
