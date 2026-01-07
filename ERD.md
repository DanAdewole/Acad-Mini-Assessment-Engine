# Entity Relationship Diagram (ERD)

This document contains the database schema for the Mini Assessment Engine.

---

## Database Schema

```mermaid
erDiagram
    User ||--o{ Course : instructs
    User ||--o{ Submission : submits
    Course ||--o{ Exam : contains
    Exam ||--o{ Question : has
    Exam ||--o{ Submission : receives
    Submission ||--o{ Answer : includes
    Question ||--o{ Answer : answered_by

    User {
        int id PK
        string email UK
        string password
        string first_name
        string last_name
        enum role "student, instructor, admin"
        boolean is_active
        boolean is_staff
        boolean is_superuser
        datetime created_at
        datetime updated_at
    }

    Course {
        int id PK
        string code UK
        string title
        text description
        int instructor_id FK
        boolean is_published
        json metadata
        datetime created_at
        datetime updated_at
    }

    Exam {
        int id PK
        int course_id FK
        string title
        text description
        int duration_minutes
        datetime start_time
        datetime end_time
        boolean is_published
        json metadata
        datetime created_at
        datetime updated_at
    }

    Question {
        int id PK
        int exam_id FK
        enum question_type "multiple_choice, true_false, short_answer, essay"
        text question_text
        json expected_answer
        json options
        float points
        int order
        json metadata
        datetime created_at
        datetime updated_at
    }

    Submission {
        int id PK
        int user_id FK
        int exam_id FK
        datetime submitted_at
        datetime graded_at
        float total_score
        float max_score
        enum status "in_progress, submitted, graded"
        json metadata
        datetime created_at
        datetime updated_at
    }

    Answer {
        int id PK
        int submission_id FK
        int question_id FK
        text answer_text
        json answer_data
        float score
        float max_score
        json grading_feedback
        datetime created_at
        datetime updated_at
    }
```

---

## Key Relationships

### One-to-Many Relationships:

-   **User → Course**: One instructor teaches many courses
-   **User → Submission**: One student makes many submissions
-   **Course → Exam**: One course has many exams
-   **Exam → Question**: One exam has many questions
-   **Exam → Submission**: One exam receives many submissions
-   **Submission → Answer**: One submission has many answers
-   **Question → Answer**: One question has many answers (from different students)

### Constraints:

-   `User.email`: Unique
-   `Course.code`: Unique
-   `(Submission.user_id, Submission.exam_id)`: Unique Together (one submission per user per exam)
-   `(Answer.submission_id, Answer.question_id)`: Unique Together (one answer per question per submission)

### Indexes:

-   Primary keys on all `id` fields
-   Foreign keys on all relationship fields
-   `User.email`, `User.role`
-   `Course.code`, `Course.instructor_id`, `Course.is_published`
-   `Exam.course_id`, `Exam.is_published`, `Exam.start_time`, `Exam.end_time`
-   `Question.exam_id`, `Question.question_type`, `Question.order`
-   `Submission.user_id`, `Submission.exam_id`, `Submission.status`, `Submission.submitted_at`
-   `Answer.submission_id`, `Answer.question_id`

---

## Database Models Summary

| Model          | Description                        | Key Fields                                        |
| -------------- | ---------------------------------- | ------------------------------------------------- |
| **User**       | Authentication and user management | email (unique), role, password                    |
| **Course**     | Academic courses                   | code (unique), instructor, is_published           |
| **Exam**       | Assessments within courses         | course, title, start_time, end_time, is_published |
| **Question**   | Individual exam questions          | exam, question_type, points, expected_answer      |
| **Submission** | Student exam attempts              | user, exam, status, total_score                   |
| **Answer**     | Individual answers in submissions  | submission, question, score, grading_feedback     |

---

## Question Types

The system supports 4 question types:

1. **Multiple Choice** - Single correct answer from multiple options
2. **True/False** - Binary choice questions
3. **Short Answer** - Brief text responses
4. **Essay** - Extended written responses

---

## Grading Flow

```mermaid
graph LR
    A[Student Submits Exam] --> B[Create Submission]
    B --> C[Create Answers]
    C --> D[Select Grading Service]
    D --> E{Service Type}
    E -->|Mock| F[TF-IDF Grading]
    E -->|AI| G[OpenAI Grading]
    E -->|Gemini| H[Gemini Grading]
    F --> I[Update Scores]
    G --> I
    H --> I
    I --> J[Mark as Graded]
    J --> K[Return Results]
```

---

## Notes

-   **Database**: PostgreSQL (production) or SQLite (development)
-   **ORM**: Django ORM with query optimization (select_related, prefetch_related)
-   **JSON Fields**: Used for flexible data storage (metadata, options, answers)
-   **Timestamps**: All models include created_at and updated_at
-   **Soft Deletes**: Not implemented (hard deletes with CASCADE)
