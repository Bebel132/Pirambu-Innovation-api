from datetime import datetime, timedelta
from app import create_app
from extensions import db
from models.Courses import CourseModel

app = create_app()

with app.app_context():
    limit_date = datetime.utcnow() - timedelta(days=30)

    courses_to_delete = CourseModel.query.filter(
        CourseModel.active == False,
        CourseModel.deactivated_at != None,
        CourseModel.deactivated_at <= limit_date
    ).all()

    for course in courses_to_delete:
        db.session.delete(course)

    db.session.commit()

    print(f"{len(courses_to_delete)} cursos removidos definitivamente.")
