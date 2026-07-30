def test_register_and_login(client):
    """Test user registration and subsequent login."""
    res_reg = client.post("/auth/register", data={
        "name": "Jane Developer",
        "email": "jane@example.com",
        "password": "securepassword",
        "confirm_password": "securepassword"
    }, follow_redirects=True)
    assert res_reg.status_code == 200
    assert b"Registration successful" in res_reg.data

    res_login = client.post("/auth/login", data={
        "email": "jane@example.com",
        "password": "securepassword"
    }, follow_redirects=True)
    assert res_login.status_code == 200
    assert b"Welcome back, Jane Developer" in res_login.data


def test_invalid_login(client):
    """Test login with incorrect password."""
    res = client.post("/auth/login", data={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    }, follow_redirects=True)
    assert b"Invalid email or password" in res.data
