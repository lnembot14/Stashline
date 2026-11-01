from flask import Blueprint, request


saved_track_route = Blueprint("saved_track_route", __name__)

# Saved entries have no editable metadata yet.
EDITABLE_FIELDS = {}
# Temporary until user_id comes from verified authentication.
CREATE_FIELDS = {'user_id': 'uuid', 'track_id': 'uuid'}
RESPONSE_FIELDS = ('id', 'user_id', 'track_id', 'saved_at')


@saved_track_route.route('/saved_tracks', methods=['GET', 'POST'])
def saved_tracks():
    if request.method == 'GET':
        # TODO: List the authenticated user's saved tracks.
        
        pass

    if request.method == 'POST':
        # TODO: Save a track for the authenticated user.
        pass


@saved_track_route.route('/saved_tracks/<uuid:saved_track_id>', methods=['GET', 'PATCH', 'DELETE'])
def saved_track_detail(saved_track_id):
    if request.method == 'GET':
        # TODO: Retrieve a saved track belonging to the authenticated user.
        pass

    if request.method == 'PATCH':
        # TODO: Validate and apply allowed updates to the saved track.
        pass

    if request.method == 'DELETE':
        # TODO: Remove a saved track belonging to the authenticated user.
        pass
