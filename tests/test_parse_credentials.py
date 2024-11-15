from supadef.credentials import parse_credentials


def test_parse_credentials():
    creds = parse_credentials('tests/test_credentials.yml')
    assert creds
    assert 'default' in creds
    assert ':' in creds['default']

    key_id, key = creds['default'].split(':')

    assert key_id == 'my_id'
    assert key == 'asdfasdfasdf'
