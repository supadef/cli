from supadef.credentials import parse_credentials


def test_parse_credentials():
    creds = parse_credentials('tests/test_credentials.yml')
    assert creds
    assert 'uid' in creds
    assert 'api_key' in creds
