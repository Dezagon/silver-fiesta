from fastapi import Depends, FastAPI, status, HTTPException
from sqlmodel import Session, select

from database import get_db
from models import Course, Instructor, Student
from schemas import AddStudentToCourseRequest, CreateStudentRequest, CreateInstructorRequest, CreateCourseRequest

app = FastAPI()

# GET STUDENTS

@app.get("/students")
async def get_students(db: Session = Depends(get_db)) -> list[Student]:
    return db.exec(select(Student)).all()

# GET INSTRUCTORS

@app.get("/instructors")
async def get_instructors(db: Session = Depends(get_db)) -> list[Instructor]:
    return db.exec(select(Instructor)).all()


# GET COURSES
@app.get("/courses")
async def get_courses(db: Session = Depends(get_db)) -> list[Course]:
    return db.exec(select(Course)).all()

# GET STUDENTS BY COURSE ID
@app.get("/courses/{course_id}/students")
async def get_course_student_list(course_id: int, db: Session = Depends(get_db)) -> list[Student]:
    course: Course | None = db.get(Course, course_id)
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course with ID {course_id} not found.")
    return course.students


# POST STUDENTS
@app.post("/students", status_code=status.HTTP_201_CREATED)
async def create_student(create_student_request: CreateStudentRequest, db: Session = Depends(get_db)) -> None:
    student: Student = Student(name=create_student_request.name)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student.id

# POST INSTRUCTOR
@app.post("/instructors", status_code=status.HTTP_201_CREATED)
async def create_instructor(create_instructor_request: CreateInstructorRequest, db: Session = Depends(get_db)) -> None:
    instructor: Instructor = Instructor(name=create_instructor_request.name)
    db.add(instructor)
    db.commit()
    db.refresh(instructor)
    return instructor.id

# POST COURSE
@app.post("/courses", status_code=status.HTTP_201_CREATED)
async def create_course(create_course_request: CreateCourseRequest, db: Session = Depends(get_db)) -> None:
    # Make sure instructor exists
    instructor: Instructor | None = db.get(Instructor, create_course_request.instructor_id)
    if instructor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No instructor with ID {create_course_request.instructor_id} found.")
    course: Course = Course(**create_course_request.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course.id

@app.post("/courses/{course_id}/students", status_code=status.HTTP_201_CREATED)
async def add_student_to_course(course_id: int, request: AddStudentToCourseRequest, db: Session = Depends(get_db)) -> None:
    # Get student
    student: Student | None = db.get(Student, request.student_id)


    # Get course
    course: Course | None = db.get(Course, course_id)


    # Check if student exists
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student with ID of {request.student_id} not found")


    # Check if course exists
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Course with ID {course.course_id} not found")


    # Check if student is already in course
    if student in course.students:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Student already in course")

    # Add student to course
    course.students.append(student)
    db.commit()