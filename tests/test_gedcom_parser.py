from gedcom.GedcomParser import GedcomParser


def test_parse_valid_gedcom_row():
    check_gedcom_line('0 NOTE dates after now', True)


def test_parse_valid_gedcom_row_2():
    check_gedcom_line('0 bi00 INDI', True)


def test_parse_valid_gedcom_row_3():
    check_gedcom_line('1 NAME Jimmy /Conners/', True)


def test_parse_valid_gedcom_row_4():
    check_gedcom_line('0 id1 INDI', True)


def test_parse_valid_gedcom_row_5():
    check_gedcom_line('1 NAME Ned Stark', True)


def test_parse_invalid_gedcom_row():
    check_gedcom_line('1 SOUR Family Echo', False)


def test_parse_invalid_gedcom_row2():
    check_gedcom_line('2 WWW http://www.familyecho.com', False)


def test_parse_invalid_gedcom_row3():
    check_gedcom_line('1 id1 INDI', False)


def test_parse_invalid_gedcom_row4():
    check_gedcom_line('0 NAME Ned Stark', False)


def check_gedcom_line(line, is_valid):
    gedcom_parser = GedcomParser()
    assert gedcom_parser.line_to_GedcomRow(line).valid == is_valid
