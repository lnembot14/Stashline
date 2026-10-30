"""Endpoint tests using a temporary in-memory database, never DATABASE_URL."""

import unittest
from unittest.mock import patch
from uuid import uuid4

from flask import Flask
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError

from models.extensions import db
from routes.artist_routes import artist_route
from routes.eras_routes import eras_routes
from routes.tracks_routes import track_route
from routes.sources_routes import source_route


class RouteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite://")
        db.init_app(self.app)
        for blueprint in (artist_route, eras_routes, track_route, source_route):
            self.app.register_blueprint(blueprint)
        self.context = self.app.app_context()
        self.context.push()

        # SQLite must explicitly enable foreign keys to test parent deletion.
        @event.listens_for(db.engine, "connect")
        def enable_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")

        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()

    def create(self, path, values):
        response = self.client.post(path, json=values)
        self.assertEqual(response.status_code, 201, response.data)
        return response.get_json()

    def seed(self):
        artist = self.create('/artists', {'name': 'Artist', 'user_id': 'tester'})
        era = self.create('/eras', {'name': 'Era', 'user_id': 'tester', 'artist_id': artist['id']})
        track = self.create('/tracks', {
            'title': 'Song', 'notes': 'Original notes', 'user_id': 'tester', 'era_id': era['id'],
        })
        source = self.create('/sources', {
            'platform': 'YouTube', 'url': 'https://example.com/song',
            'quality': 'MP3', 'upload_date': '2026-10-30T10:00:00-04:00',
            'user_id': 'tester', 'track_id': track['id'],
        })
        return dict(artists=artist, eras=era, tracks=track, sources=source)

    def test_create_list_and_individual_get(self):
        for resource, record in self.seed().items():
            with self.subTest(resource=resource):
                response = self.client.get(f'/{resource}/{record["id"]}')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.get_json(), record)
                self.assertEqual(len(self.client.get(f'/{resource}').get_json()), 1)

    def test_partial_updates_and_optional_fields(self):
        records = self.seed()
        changes = {
            'artists': {'name': ' New artist '},
            'eras': {'name': 'New era'},
            'tracks': {'notes': None},
            'sources': {'quality': 'FLAC', 'upload_date': None},
        }
        for resource, updates in changes.items():
            with self.subTest(resource=resource):
                record = records[resource]
                path = f'/{resource}/{record["id"]}'
                response = self.client.patch(path, json=updates)
                self.assertEqual(response.status_code, 200, response.data)
                expected = {**record, **updates}
                if resource == 'artists':
                    expected['name'] = 'New artist'
                self.assertEqual(self.client.get(path).get_json(), expected)

    def test_request_validation(self):
        records = self.seed()
        for resource, record in records.items():
            with self.subTest(resource=resource):
                collection = f'/{resource}'
                detail = f'{collection}/{record["id"]}'
                for path, method in ((collection, self.client.post), (detail, self.client.patch)):
                    for payload in ({}, [], {'unknown': 'value'}):
                        self.assertEqual(method(path, json=payload).status_code, 400)
                    self.assertEqual(method(path, data='text').status_code, 415)
                    self.assertEqual(method(path, data='{', content_type='application/json').status_code, 400)
                self.assertEqual(self.client.patch(detail, json={'user_id': 'other'}).status_code, 400)
                self.assertEqual(self.client.get(detail).get_json(), record)

    def test_invalid_values_and_parent_ids(self):
        records = self.seed()
        for resource, field in (('artists', 'name'), ('eras', 'name'), ('tracks', 'title'), ('sources', 'url')):
            path = f'/{resource}/{records[resource]["id"]}'
            for value in (None, 123, ' '):
                self.assertEqual(self.client.patch(path, json={field: value}).status_code, 400)
        source_path = f'/sources/{records["sources"]["id"]}'
        self.assertEqual(self.client.patch(source_path, json={'upload_date': 'bad'}).status_code, 400)
        for parent_id in ('invalid-uuid', str(uuid4())):
            self.assertEqual(self.client.post('/eras', json={
                'name': 'Invalid', 'user_id': 'tester', 'artist_id': parent_id,
            }).status_code, 400)
        # A failed insert must roll back so the next request can succeed.
        self.assertEqual(len(self.client.get('/eras').get_json()), 1)

    def test_delete_conflicts_success_and_missing_records(self):
        records = self.seed()
        for resource in ('artists', 'eras', 'tracks'):
            path = f'/{resource}/{records[resource]["id"]}'
            self.assertEqual(self.client.delete(path).status_code, 409)
            self.assertEqual(self.client.get(path).status_code, 200)
        # Delete from the bottom of the hierarchy upward.
        for resource in ('sources', 'tracks', 'eras', 'artists'):
            path = f'/{resource}/{records[resource]["id"]}'
            self.assertEqual(self.client.delete(path).status_code, 200)
            self.assertEqual(self.client.get(path).status_code, 404)
            self.assertEqual(self.client.patch(path, json={'name': 'Missing'} if resource in ('artists', 'eras')
                                               else {'title': 'Missing'} if resource == 'tracks'
                                               else {'quality': 'FLAC'}).status_code, 404)
            self.assertEqual(self.client.delete(path).status_code, 404)

    def test_unexpected_database_error_rolls_back(self):
        records = self.seed()
        path = f'/sources/{records["sources"]["id"]}'
        with patch.object(db.session, 'commit', side_effect=SQLAlchemyError('test failure')):
            with self.assertLogs(self.app.logger, level='ERROR'):
                self.assertEqual(self.client.patch(path, json={'quality': 'FLAC'}).status_code, 500)
        self.assertEqual(self.client.get(path).get_json()['quality'], 'MP3')


if __name__ == '__main__':
    unittest.main()
