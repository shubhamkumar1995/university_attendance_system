from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import SessionLocal
from models import  User, Department, Student, Course, AttendanceLog
from utils import hash_password


app = FastAPI(title="University Attendance System")



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "API is running"}


# --------------- Pydantic Schemas ---------------

class UserBase(BaseModel):
    type: Optional[str]
    full_name: Optional[str]
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    type: Optional[str]
    full_name: Optional[str]
    password: Optional[str]

class UserOut(BaseModel):
    id: int
    type: str
    full_name: str
    username: str
    email: str
    updated_at: datetime

    class Config:
        orm_mode = True

# Department schemas
class DepartmentBase(BaseModel):
    department_name: str
    submitted_by: int

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    department_name: Optional[str]

class DepartmentOut(DepartmentBase):
    id: int
    updated_at: datetime
    class Config:
        orm_mode = True

# Student schemas
class StudentBase(BaseModel):
    full_name: str
    department_id: int
    class_: Optional[str]
    submitted_by: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    full_name: Optional[str]
    department_id: Optional[int]
    class_: Optional[str]

class StudentOut(StudentBase):
    id: int
    updated_at: datetime
    class Config:
        orm_mode = True

# Course schemas
class CourseBase(BaseModel):
    course_name: str
    department_id: int
    semester: Optional[str]
    class_: Optional[str]
    lecture_hours: Optional[int]
    submitted_by: int

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    course_name: Optional[str]
    department_id: Optional[int]
    semester: Optional[str]
    class_: Optional[str]
    lecture_hours: Optional[int]

class CourseOut(CourseBase):
    id: int
    updated_at: datetime
    class Config:
        orm_mode = True

# AttendanceLog schemas
class AttendanceLogBase(BaseModel):
    student_id: int
    course_id: int
    present: bool
    submitted_by: int

class AttendanceLogCreate(AttendanceLogBase):
    pass

class AttendanceLogUpdate(BaseModel):
    present: Optional[bool]

class AttendanceLogOut(AttendanceLogBase):
    id: int
    updated_at: datetime
    class Config:
        orm_mode = True

# --------------- API Endpoints ---------------

# -------- User --------
@app.post("/users/", response_model=UserOut)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    stmt = select(User).where((User.email == user.email) | (User.username == user.username))
    result = await db.execute(stmt)
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email or Username already registered")
    new_user = User(
        type=user.type,
        full_name=user.full_name,
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        updated_at=datetime.utcnow()
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for var, value in vars(user_update).items():
        if value is not None:
            setattr(user, var, value)
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user

# -------- Department --------
@app.post("/departments/", response_model=DepartmentOut)
def create_department(dept: DepartmentCreate, db: Session = Depends(get_db)):
    new_dept = Department(
        department_name=dept.department_name,
        submitted_by=dept.submitted_by,
        updated_at=datetime.utcnow()
    )
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept

@app.get("/departments/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).get(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept

@app.put("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(dept_id: int, dept_update: DepartmentUpdate, db: Session = Depends(get_db)):
    dept = db.query(Department).get(dept_id)
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    for var, value in vars(dept_update).items():
        if value is not None:
            setattr(dept, var, value)
    dept.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(dept)
    return dept

# -------- Student --------
@app.post("/students/", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(
        full_name=student.full_name,
        department_id=student.department_id,
        class_=student.class_,
        submitted_by=student.submitted_by,
        updated_at=datetime.utcnow()
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    for var, value in vars(student_update).items():
        if value is not None:
            setattr(student, var, value)
    student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(student)
    return student

# -------- Course --------
@app.post("/courses/", response_model=CourseOut)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    new_course = Course(
        course_name=course.course_name,
        department_id=course.department_id,
        semester=course.semester,
        class_=course.class_,
        lecture_hours=course.lecture_hours,
        submitted_by=course.submitted_by,
        updated_at=datetime.utcnow()
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@app.get("/courses/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.put("/courses/{course_id}", response_model=CourseOut)
def update_course(course_id: int, course_update: CourseUpdate, db: Session = Depends(get_db)):
    course = db.query(Course).get(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for var, value in vars(course_update).items():
        if value is not None:
            setattr(course, var, value)
    course.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(course)
    return course

# -------- AttendanceLog --------
@app.post("/attendance/", response_model=AttendanceLogOut)
def create_attendance(attendance: AttendanceLogCreate, db: Session = Depends(get_db)):
    new_attendance = AttendanceLog(
        student_id=attendance.student_id,
        course_id=attendance.course_id,
        present=attendance.present,
        submitted_by=attendance.submitted_by,
        updated_at=datetime.utcnow()
    )
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance

@app.get("/attendance/{attendance_id}", response_model=AttendanceLogOut)
def get_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = db.query(AttendanceLog).get(attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="AttendanceLog not found")
    return attendance

@app.put("/attendance/{attendance_id}", response_model=AttendanceLogOut)
def update_attendance(attendance_id: int, attendance_update: AttendanceLogUpdate, db: Session = Depends(get_db)):
    attendance = db.query(AttendanceLog).get(attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="AttendanceLog not found")
    for var, value in vars(attendance_update).items():
        if value is not None:
            setattr(attendance, var, value)
    attendance.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(attendance)
    return attendance