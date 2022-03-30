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

from squiggy.api.api_util import can_update_whiteboard
from squiggy.lib.errors import BadRequestError, ResourceNotFoundError
from squiggy.models.whiteboard import Whiteboard
from squiggy.models.whiteboard_element import WhiteboardElement


def create_whiteboard_elements(user, whiteboard_id, whiteboard_elements):
    whiteboard = Whiteboard.find_by_id(whiteboard_id) if whiteboard_id else None
    if not whiteboard:
        raise ResourceNotFoundError('Whiteboard not found.')
    if whiteboard['deletedAt']:
        raise ResourceNotFoundError('Whiteboard is read-only.')
    if not len(whiteboard_elements):
        raise BadRequestError('One or more whiteboard-elements required')
    if not can_update_whiteboard(user=user, whiteboard=whiteboard):
        raise BadRequestError('To update a whiteboard you must own it or be a teacher in the course.')
    if _has_canvas(whiteboard_elements) and _has_canvas(whiteboard['whiteboardElements']):
        raise BadRequestError('Whiteboard can have one, and only one, element of type canvas.')

    def _create(whiteboard_element):
        return WhiteboardElement.create(
            asset_id=whiteboard_element.get('assetId', None),
            element=whiteboard_element['element'],
            whiteboard_id=whiteboard_id,
        )
    return [_create(whiteboard_element) for whiteboard_element in whiteboard_elements]


def _has_canvas(elements):
    return 'canvas' in [e.get('type') for e in elements]