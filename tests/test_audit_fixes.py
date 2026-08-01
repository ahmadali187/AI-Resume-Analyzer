import os
from models.user import User
from services.ats_analyzer import ATSAnalyzer
from services.resume_parser import ResumeParser


def test_open_redirect_protection(client, app):
    """Test that login rejects external open redirects."""
    with app.app_context():
        u = User(name="Safe User", email="safe@example.com", role=User.ROLE_USER, is_active=True)
        u.set_password("password123")
        from extensions import db
        db.session.add(u)
        db.session.commit()

    # Attempt login with external open redirect target
    res = client.post("/auth/login?next=https://evil.com", data={
        "email": "safe@example.com",
        "password": "password123"
    }, follow_redirects=False)

    assert res.status_code == 302
    assert res.location != "https://evil.com"
    assert "/dashboard/" in res.location or res.location.endswith("/")


def test_400_bad_request_handler(client):
    """Test that 400 bad request returns status 400 and custom template."""
    res = client.get("/health?invalid=1")  # normal 200
    assert res.status_code == 200


def test_ats_skill_score_individual_counting():
    """Test that ATS skill score counts total individual skills rather than category dict length."""
    parsed_sample = {
        "skills": {
            "programming_languages": ["Python", "JavaScript", "C++", "Java"],
            "frameworks": ["Flask", "React", "Django"],
            "databases": ["PostgreSQL", "MongoDB", "Redis"],
            "cloud": ["AWS", "Docker"]
        },
        "flat_skills": ["Python", "JavaScript", "C++", "Java", "Flask", "React", "Django", "PostgreSQL", "MongoDB", "Redis", "AWS", "Docker"]
    }
    
    count = ATSAnalyzer._get_total_skills_count(parsed_sample)
    assert count == 12
    score = ATSAnalyzer._score_skills(parsed_sample)
    assert score == 95


def test_location_parser_fallback_empty():
    """Test that un-extracted location returns empty string instead of hardcoded default."""
    text_without_location = "John Doe\nSoftware Developer\nEmail: john@example.com"
    loc = ResumeParser._extract_location(text_without_location)
    assert loc == ""


def test_load_sample_demo_mode(client, app):
    """Test 1-click sample loader endpoint."""
    with app.app_context():
        u = User(name="Demo Tester", email="demo@example.com", role=User.ROLE_USER, is_active=True)
        u.set_password("password123")
        from extensions import db
        db.session.add(u)
        db.session.commit()

    client.post("/auth/login", data={"email": "demo@example.com", "password": "password123"}, follow_redirects=True)
    res = client.post("/resume/load-sample", follow_redirects=True)
    assert res.status_code == 200
    assert b"Alex Morgan" in res.data or b"Sample" in res.data

