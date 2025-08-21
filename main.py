# GraphQL Resume API with FastAPI + Strawberry
# Simple implementation for Users, Education, and Job Experience

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from strawberry.scalars import JSON
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
import uuid
import asyncio

# Database imports
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, String, Text, DateTime, Date, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.future import select
from sqlalchemy import and_
import os
from dotenv import load_dotenv

# Pydantic for validation
from pydantic import BaseModel, EmailStr, Field

# Load environment variables
load_dotenv()

# Database configuration
class DatabaseConfig:
    """Database configuration from environment variables"""
    def __init__(self):
        self.host = os.getenv("DB_HOST", "tanner-postgres.ct04w2k200ji.us-east-2.rds.amazonaws.com")
        self.port = os.getenv("DB_PORT", "5432")
        self.database = os.getenv("DB_NAME", "resume_db")
        self.username = os.getenv("DB_USERNAME")
        self.password = os.getenv("DB_PASSWORD")
        
        if not self.username or not self.password:
            raise ValueError("DB_USERNAME and DB_PASSWORD must be set in environment variables")
    
    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

# Database setup
db_config = DatabaseConfig()
engine = create_async_engine(db_config.url, echo=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# Database Models
class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class EducationModel(Base):
    __tablename__ = "education"
    
    education_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    institution_name = Column(String(255), nullable=False)
    location = Column(String(255))
    date_started = Column(Date, nullable=False)
    date_finished = Column(Date)
    major = Column(String(255))
    minor = Column(String(255))
    gpa = Column(Numeric(3, 2))
    details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class JobExperienceModel(Base):
    __tablename__ = "job_experience"
    
    job_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(255))
    location = Column(String(255))
    date_started = Column(Date, nullable=False)
    date_left = Column(Date)
    details = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow)

# Database dependency
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# GraphQL Types
@strawberry.type
class User:
    user_id: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def education(self, info: Info) -> List["Education"]:
        """Get all education records for this user"""
        session = info.context["db_session"]
        result = await session.execute(
            select(EducationModel).where(EducationModel.user_id == self.user_id)
        )
        education_records = result.scalars().all()
        
        return [
            Education(
                education_id=str(edu.education_id),
                user_id=str(edu.user_id),
                institution_name=edu.institution_name,
                location=edu.location,
                date_started=edu.date_started,
                date_finished=edu.date_finished,
                major=edu.major,
                minor=edu.minor,
                gpa=float(edu.gpa) if edu.gpa else None,
                details=edu.details,
                created_at=edu.created_at,
                updated_at=edu.updated_at,
            )
            for edu in education_records
        ]
    
    @strawberry.field
    async def job_experience(self, info: Info) -> List["JobExperience"]:
        """Get all job experience records for this user"""
        session = info.context["db_session"]
        result = await session.execute(
            select(JobExperienceModel).where(JobExperienceModel.user_id == self.user_id)
        )
        job_records = result.scalars().all()
        
        return [
            JobExperience(
                job_id=str(job.job_id),
                user_id=str(job.user_id),
                company_name=job.company_name,
                job_title=job.job_title,
                location=job.location,
                date_started=job.date_started,
                date_left=job.date_left,
                details=job.details,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            for job in job_records
        ]

@strawberry.type
class Education:
    education_id: str
    user_id: str
    institution_name: str
    location: Optional[str] = None
    date_started: date
    date_finished: Optional[date] = None
    major: Optional[str] = None
    minor: Optional[str] = None
    gpa: Optional[float] = None
    details: Optional[JSON] = None
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def user(self, info: Info) -> Optional[User]:
        """Get the user who owns this education record"""
        session = info.context["db_session"]
        result = await session.execute(
            select(UserModel).where(UserModel.user_id == self.user_id)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return User(
                user_id=str(user_model.user_id),
                email=user_model.email,
                full_name=user_model.full_name,
                created_at=user_model.created_at,
                updated_at=user_model.updated_at,
            )
        return None

@strawberry.type
class JobExperience:
    job_id: str
    user_id: str
    company_name: str
    job_title: Optional[str] = None
    location: Optional[str] = None
    date_started: date
    date_left: Optional[date] = None
    details: Optional[JSON] = None
    created_at: datetime
    updated_at: datetime
    
    @strawberry.field
    async def user(self, info: Info) -> Optional[User]:
        """Get the user who owns this job experience record"""
        session = info.context["db_session"]
        result = await session.execute(
            select(UserModel).where(UserModel.user_id == self.user_id)
        )
        user_model = result.scalar_one_or_none()
        
        if user_model:
            return User(
                user_id=str(user_model.user_id),
                email=user_model.email,
                full_name=user_model.full_name,
                created_at=user_model.created_at,
                updated_at=user_model.updated_at,
            )
        return None

# Input Types for Mutations
@strawberry.input
class CreateUserInput:
    email: str
    full_name: Optional[str] = None
    password: str

@strawberry.input
class UpdateUserInput:
    email: Optional[str] = None
    full_name: Optional[str] = None

@strawberry.input
class CreateEducationInput:
    user_id: str
    institution_name: str
    location: Optional[str] = None
    date_started: date
    date_finished: Optional[date] = None
    major: Optional[str] = None
    minor: Optional[str] = None
    gpa: Optional[float] = None
    details: Optional[JSON] = None

@strawberry.input
class UpdateEducationInput:
    institution_name: Optional[str] = None
    location: Optional[str] = None
    date_started: Optional[date] = None
    date_finished: Optional[date] = None
    major: Optional[str] = None
    minor: Optional[str] = None
    gpa: Optional[float] = None
    details: Optional[JSON] = None

@strawberry.input
class CreateJobExperienceInput:
    user_id: str
    company_name: str
    job_title: Optional[str] = None
    location: Optional[str] = None
    date_started: date
    date_left: Optional[date] = None
    details: Optional[JSON] = None

@strawberry.input
class UpdateJobExperienceInput:
    company_name: Optional[str] = None
    job_title: Optional[str] = None
    location: Optional[str] = None
    date_started: Optional[date] = None
    date_left: Optional[date] = None
    details: Optional[JSON] = None

# Response Types
@strawberry.type
class CreateUserResponse:
    success: bool
    message: str
    user: Optional[User] = None

@strawberry.type
class CreateEducationResponse:
    success: bool
    message: str
    education: Optional[Education] = None

@strawberry.type
class CreateJobExperienceResponse:
    success: bool
    message: str
    job_experience: Optional[JobExperience] = None

# GraphQL Queries
@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info: Info) -> List[User]:
        """Get all users"""
        session = info.context["db_session"]
        result = await session.execute(select(UserModel))
        users = result.scalars().all()
        
        return [
            User(
                user_id=str(user.user_id),
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            for user in users
        ]
    
    @strawberry.field
    async def user(self, info: Info, user_id: str) -> Optional[User]:
        """Get a specific user by ID"""
        session = info.context["db_session"]
        result = await session.execute(
            select(UserModel).where(UserModel.user_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            return User(
                user_id=str(user.user_id),
                email=user.email,
                full_name=user.full_name,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        return None
    
    @strawberry.field
    async def education_records(self, info: Info, user_id: Optional[str] = None) -> List[Education]:
        """Get education records, optionally filtered by user"""
        session = info.context["db_session"]
        
        if user_id:
            result = await session.execute(
                select(EducationModel).where(EducationModel.user_id == user_id)
            )
        else:
            result = await session.execute(select(EducationModel))
        
        education_records = result.scalars().all()
        
        return [
            Education(
                education_id=str(edu.education_id),
                user_id=str(edu.user_id),
                institution_name=edu.institution_name,
                location=edu.location,
                date_started=edu.date_started,
                date_finished=edu.date_finished,
                major=edu.major,
                minor=edu.minor,
                gpa=float(edu.gpa) if edu.gpa else None,
                details=edu.details,
                created_at=edu.created_at,
                updated_at=edu.updated_at,
            )
            for edu in education_records
        ]
    
    @strawberry.field
    async def job_experiences(self, info: Info, user_id: Optional[str] = None) -> List[JobExperience]:
        """Get job experiences, optionally filtered by user"""
        session = info.context["db_session"]
        
        if user_id:
            result = await session.execute(
                select(JobExperienceModel).where(JobExperienceModel.user_id == user_id)
            )
        else:
            result = await session.execute(select(JobExperienceModel))
        
        job_records = result.scalars().all()
        
        return [
            JobExperience(
                job_id=str(job.job_id),
                user_id=str(job.user_id),
                company_name=job.company_name,
                job_title=job.job_title,
                location=job.location,
                date_started=job.date_started,
                date_left=job.date_left,
                details=job.details,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )
            for job in job_records
        ]

# GraphQL Mutations
@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_user(self, info: Info, input: CreateUserInput) -> CreateUserResponse:
        """Create a new user"""
        session = info.context["db_session"]
        
        try:
            # Simple password hashing (use proper hashing in production)
            password_hash = f"hashed_{input.password}"
            
            new_user = UserModel(
                email=input.email,
                full_name=input.full_name,
                password_hash=password_hash
            )
            
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            
            return CreateUserResponse(
                success=True,
                message="User created successfully",
                user=User(
                    user_id=str(new_user.user_id),
                    email=new_user.email,
                    full_name=new_user.full_name,
                    created_at=new_user.created_at,
                    updated_at=new_user.updated_at,
                )
            )
        
        except Exception as e:
            await session.rollback()
            return CreateUserResponse(
                success=False,
                message=f"Error creating user: {str(e)}"
            )
    
    @strawberry.mutation
    async def create_education(self, info: Info, input: CreateEducationInput) -> CreateEducationResponse:
        """Create a new education record"""
        session = info.context["db_session"]
        
        try:
            new_education = EducationModel(
                user_id=input.user_id,
                institution_name=input.institution_name,
                location=input.location,
                date_started=input.date_started,
                date_finished=input.date_finished,
                major=input.major,
                minor=input.minor,
                gpa=Decimal(str(input.gpa)) if input.gpa else None,
                details=input.details
            )
            
            session.add(new_education)
            await session.commit()
            await session.refresh(new_education)
            
            return CreateEducationResponse(
                success=True,
                message="Education record created successfully",
                education=Education(
                    education_id=str(new_education.education_id),
                    user_id=str(new_education.user_id),
                    institution_name=new_education.institution_name,
                    location=new_education.location,
                    date_started=new_education.date_started,
                    date_finished=new_education.date_finished,
                    major=new_education.major,
                    minor=new_education.minor,
                    gpa=float(new_education.gpa) if new_education.gpa else None,
                    details=new_education.details,
                    created_at=new_education.created_at,
                    updated_at=new_education.updated_at,
                )
            )
        
        except Exception as e:
            await session.rollback()
            return CreateEducationResponse(
                success=False,
                message=f"Error creating education record: {str(e)}"
            )
    
    @strawberry.mutation
    async def create_job_experience(self, info: Info, input: CreateJobExperienceInput) -> CreateJobExperienceResponse:
        """Create a new job experience record"""
        session = info.context["db_session"]
        
        try:
            new_job = JobExperienceModel(
                user_id=input.user_id,
                company_name=input.company_name,
                job_title=input.job_title,
                location=input.location,
                date_started=input.date_started,
                date_left=input.date_left,
                details=input.details
            )
            
            session.add(new_job)
            await session.commit()
            await session.refresh(new_job)
            
            return CreateJobExperienceResponse(
                success=True,
                message="Job experience created successfully",
                job_experience=JobExperience(
                    job_id=str(new_job.job_id),
                    user_id=str(new_job.user_id),
                    company_name=new_job.company_name,
                    job_title=new_job.job_title,
                    location=new_job.location,
                    date_started=new_job.date_started,
                    date_left=new_job.date_left,
                    details=new_job.details,
                    created_at=new_job.created_at,
                    updated_at=new_job.updated_at,
                )
            )
        
        except Exception as e:
            await session.rollback()
            return CreateJobExperienceResponse(
                success=False,
                message=f"Error creating job experience: {str(e)}"
            )

# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Context provider for database session
async def get_context():
    async with SessionLocal() as session:
        return {"db_session": session}

# FastAPI setup
app = FastAPI(title="Resume GraphQL API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GraphQL endpoint
graphql_app = GraphQLRouter(schema, context_getter=get_context)
app.include_router(graphql_app, prefix="/graphql")

@app.get("/")
async def root():
    return {
        "message": "Resume GraphQL API",
        "graphql_endpoint": "/graphql",
        "graphql_playground": "/graphql"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)