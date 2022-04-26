"""
Copyright ©2022. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from flask import request
from flask_socketio import emit, join_room, leave_room
from squiggy.api.whiteboard_socket_handler import delete_whiteboard_element, join_whiteboard, \
    leave_whiteboard, update_updated_at, update_whiteboard, upsert_whiteboard_element
from squiggy.lib.login_session import LoginSession
from squiggy.models.user import User
from squiggy.models.whiteboard import Whiteboard


def register_sockets(socketio):

    def _get_room(whiteboard_id):
        return f'whiteboard-{whiteboard_id}'

    @socketio.on('join')
    def socketio_join(data):
        socket_id = request.sid
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        join_whiteboard(
            current_user=LoginSession(user_id),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
        )
        room = _get_room(whiteboard_id)
        join_room(room, sid=socket_id)
        emit(
            args={
                'userId': user_id,
                'whiteboardId': whiteboard_id,
            },
            broadcast=True,
            event='join',
            include_self=False,
            skip_sid=socket_id,
            to=room,
        )

    @socketio.on('leave')
    def socketio_leave(data):
        socket_id = request.sid
        user_id = data.get('userId')
        current_user = LoginSession(user_id)
        whiteboard_id = data.get('whiteboardId')
        leave_whiteboard(
            current_user=current_user,
            socket_id=request.sid,
            whiteboard_id=whiteboard_id,
        )
        room = _get_room(whiteboard_id)
        leave_room(room, sid=socket_id)
        emit(
            args={
                'userId': user_id,
                'users': Whiteboard.find_by_id(current_user, whiteboard_id)['users'],
                'whiteboardId': whiteboard_id,
            },
            event='leave',
            include_self=False,
            skip_sid=socket_id,
            to=room,
        )

    @socketio.on('update_whiteboard')
    def socketio_update_whiteboard(data):
        socket_id = request.sid
        title = data.get('title')
        users = User.find_by_ids(data.get('userIds'))
        whiteboard_id = data.get('whiteboardId')
        update_whiteboard(
            current_user=LoginSession(data.get('userId')),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
            title=title,
            users=users,
        )
        emit(
            args={
                'title': title,
                'users': [user.to_api_json() for user in users],
                'whiteboardId': whiteboard_id,
            },
            event='update_whiteboard',
            include_self=False,
            skip_sid=socket_id,
            to=_get_room(whiteboard_id),
        )

    @socketio.on('upsert_whiteboard_element')
    def socketio_upsert_whiteboard_element(data):
        socket_id = request.sid
        user_id = data.get('userId')
        whiteboard_id = data.get('whiteboardId')
        whiteboard_element = upsert_whiteboard_element(
            current_user=LoginSession(user_id),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
            whiteboard_element=data.get('whiteboardElement'),
        )
        emit(
            args={
                'whiteboardElement': whiteboard_element,
                'whiteboardId': whiteboard_id,
            },
            event='upsert_whiteboard_element',
            include_self=False,
            skip_sid=socket_id,
            to=_get_room(whiteboard_id),
        )

    @socketio.on('delete_whiteboard_element')
    def socketio_delete(data):
        socket_id = request.sid
        whiteboard_element = data.get('whiteboardElement')
        whiteboard_id = data.get('whiteboardId')
        delete_whiteboard_element(
            current_user=LoginSession(data.get('userId')),
            socket_id=socket_id,
            whiteboard_id=whiteboard_id,
            whiteboard_element=whiteboard_element,
        )
        emit(
            args={
                'uuid': whiteboard_element['element']['uuid'],
                'whiteboardId': whiteboard_id,
            },
            event='delete_whiteboard_element',
            include_self=False,
            skip_sid=socket_id,
            to=_get_room(whiteboard_id),
        )

    @socketio.on('ping')
    def socketio_ping(data):
        return update_updated_at(
            current_user=LoginSession(data.get('userId')),
            socket_id=request.sid,
            whiteboard_id=data.get('whiteboardId'),
        )

    @socketio.on('disconnect')
    def socketio_disconnect():
        pass