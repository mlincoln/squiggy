"""
Copyright ©2021. The Regents of the University of California (Regents). All Rights Reserved.

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

from squiggy.models.course import Course


unauthorized_user_id = '666'


def _api_activate_course(client, expected_status_code=200):
    response = client.post('/api/course/activate')
    assert response.status_code == expected_status_code


def _api_get_course(client):
    response = client.get('/api/profile/my')
    return response.json['course']


class TestReactivateCourse:

    def test_anonymous(self, client):
        """Denies anonymous user."""
        _api_activate_course(client, expected_status_code=401)

    def test_unauthorized(self, client, fake_auth):
        """Denies unauthorized user."""
        fake_auth.login(unauthorized_user_id)
        _api_activate_course(client, expected_status_code=401)

    def test_student(self, client, fake_auth, student_id):
        """Denies student."""
        fake_auth.login(student_id)
        _api_activate_course(client, expected_status_code=401)

    def test_teacher(self, client, fake_auth, authorized_user_id, db_session):
        """Allows teacher."""
        fake_auth.login(authorized_user_id)
        course_feed = _api_get_course(client)
        assert course_feed['active'] is True

        db_course = db_session.query(Course).filter_by(id=course_feed['id']).first()
        db_course.active = False
        assert _api_get_course(client)['active'] is False

        _api_activate_course(client)
        assert _api_get_course(client)['active'] is True