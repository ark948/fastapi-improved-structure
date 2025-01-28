


def test_persons(dbsession):
    result = dbsession.execute("SELECT 'hello world';")
    print(result.all())
    assert 1 == 1
