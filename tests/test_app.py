from portal import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing

def test_index(client):
    with client:
        assert client.get('/').status_code == 200
        response = client.get('/')
        assert b'<h1>TSCT Portal</h1>' in response.data
        assert b'Email' in response.data
        assert b'<form method="post">' in response.data
