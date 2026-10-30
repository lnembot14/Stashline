from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from flask import Flask
from routes import sources_routes


# Use a small test app and a fake source so your real database is untouched.
app = Flask(__name__)
app.register_blueprint(sources_routes.source_route)
client = app.test_client()

source = SimpleNamespace(
    id=uuid4(),
    track_id=uuid4(),
    platform="YouTube",
    url="https://example.com/song",
    quality="MP3",
    upload_date=None,
    user_id="test-user",
    created_at=None,
)

with patch.object(sources_routes, "db") as fake_db:
    # Pretend the database found this source when the route looks up its ID.
    fake_db.session.get.return_value = source

    # Test 1: PATCH changes quality and leaves omitted fields alone.
    response = client.patch(f"/sources/{source.id}", json={"quality": "FLAC"})
    assert response.status_code == 200
    assert response.get_json()["quality"] == "FLAC"
    assert response.get_json()["platform"] == "YouTube"
    fake_db.session.commit.assert_called_once()
    print("PASS: quality changed to FLAC, platform stayed YouTube, and commit was called.")

    # Test 2: Clients cannot change ownership through this endpoint.
    fake_db.session.commit.reset_mock()
    response = client.patch(f"/sources/{source.id}", json={"user_id": "someone-else"})
    assert response.status_code == 400
    assert source.user_id == "test-user"
    fake_db.session.commit.assert_not_called()
    print("PASS: changing user_id was rejected and commit was not called.")
