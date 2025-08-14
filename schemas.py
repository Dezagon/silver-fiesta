from pydantic import BaseModel

class CreateStudentRequest(BaseModel):
    name: str

class CreateInstructorRequest(BaseModel):
    name: str

class CreateCourseRequest(BaseModel):
    name: str
    semester: str
    instructor_id: int

class AddStudentToCourseRequest(BaseModel):
    student_id: int