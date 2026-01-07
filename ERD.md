# 📊 Database Schema & Entity Relationship Diagram

This document describes the database structure and relationships for the Mini Assessment Engine.

---

## 🗂️ Database Models

### 1. **User** (`users` app)
Custom user model with role-based access control.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `email` | Email | Unique email address (used for login) |
| `password` | String | Hashed password |
| `first_name` | String | User's first name |
| `last_name` | String | User's last name |
| `role` | Choice | One of: `student`, `instructor`, `admin` |
| `is_active` | Boolean | Account status |
| `is_staff` | Boolean | Django admin access |
| `is_superuser` | Boolean | Superuser status |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Indexes:**
- `email` (unique)
- `role`

---

### 2. **Course** (`courses` app)
Represents academic courses.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `code` | String | Unique course code (e.g., "CS101") |
| `title` | String | Course title |
| `description` | Text | Course description |
| `instructor` | ForeignKey | → User (instructor) |
| `is_published` | Boolean | Published status |
| `metadata` | JSON | Additional flexible data |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Relationships:**
- `instructor` → Many courses to one User
- `exams` ← One course to many Exams

**Indexes:**
- `code` (unique)
- `instructor`
- `is_published`

**Computed Properties:**
- `is_active`: Whether course has active exams
- `active_exams_count`: Number of currently active exams

---

### 3. **Exam** (`exams` app)
Represents assessments/tests within courses.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `course` | ForeignKey | → Course |
| `title` | String | Exam title |
| `description` | Text | Exam instructions |
| `duration_minutes` | Integer | Time limit in minutes |
| `start_time` | DateTime | When exam becomes available |
| `end_time` | DateTime | When exam closes |
| `is_published` | Boolean | Published status |
| `metadata` | JSON | Additional flexible data |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Relationships:**
- `course` → Many exams to one Course
- `questions` ← One exam to many Questions
- `submissions` ← One exam to many Submissions

**Indexes:**
- `course`
- `is_published`
- `start_time`
- `end_time`
- `(course, is_published)` - Composite index

**Computed Properties:**
- `is_active`: Whether exam is currently available
- `total_points`: Sum of all question points
- `questions_count`: Number of questions in exam

---

### 4. **Question** (`exams` app)
Individual questions within exams.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `exam` | ForeignKey | → Exam |
| `question_type` | Choice | `multiple_choice`, `true_false`, `short_answer`, `essay` |
| `question_text` | Text | The question |
| `expected_answer` | JSON | Expected/correct answer |
| `options` | JSON | Options for multiple choice |
| `points` | Float | Points for this question |
| `order` | Integer | Display order |
| `metadata` | JSON | Additional flexible data |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Relationships:**
- `exam` → Many questions to one Exam
- `answers` ← One question to many Answers

**Indexes:**
- `exam`
- `question_type`
- `order`
- `(exam, order)` - Composite index

**Question Types:**

1. **Multiple Choice:**
```json
{
  "expected_answer": {"answer": "B"},
  "options": {"choices": ["A. Option 1", "B. Option 2", "C. Option 3"]}
}
```

2. **True/False:**
```json
{
  "expected_answer": {"answer": "true"}
}
```

3. **Short Answer:**
```json
{
  "expected_answer": {
    "answer": "Paris",
    "keywords": ["Paris", "paris"],
    "accept_variations": true
  }
}
```

4. **Essay:**
```json
{
  "expected_answer": {
    "answer": "Expected essay content...",
    "max_words": 500,
    "min_words": 50,
    "key_concepts": ["concept1", "concept2"]
  }
}
```

---

### 5. **Submission** (`submissions` app)
Student exam attempts.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `user` | ForeignKey | → User (student) |
| `exam` | ForeignKey | → Exam |
| `submitted_at` | DateTime | Submission timestamp |
| `graded_at` | DateTime | Grading timestamp (nullable) |
| `total_score` | Float | Total points earned |
| `max_score` | Float | Maximum possible points |
| `status` | Choice | `in_progress`, `submitted`, `graded` |
| `metadata` | JSON | Browser info, IP, etc. |
| `created_at` | DateTime | Start timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Relationships:**
- `user` → Many submissions to one User
- `exam` → Many submissions to one Exam
- `answers` ← One submission to many Answers

**Constraints:**
- `unique_together`: `(user, exam)` - One submission per user per exam

**Indexes:**
- `user`
- `exam`
- `status`
- `(user, exam)` - Composite index
- `(exam, status)` - Composite index
- `submitted_at`

**Computed Properties:**
- `percentage_score`: (total_score / max_score) * 100
- `is_passed`: percentage_score >= 60

---

### 6. **Answer** (`submissions` app)
Individual answers within submissions.

| Field | Type | Description |
|-------|------|-------------|
| `id` | Integer | Primary key |
| `submission` | ForeignKey | → Submission |
| `question` | ForeignKey | → Question |
| `answer_text` | Text | Text-based answer |
| `answer_data` | JSON | Structured answer data |
| `score` | Float | Points earned |
| `max_score` | Float | Maximum possible points |
| `grading_feedback` | JSON | Detailed feedback |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

**Relationships:**
- `submission` → Many answers to one Submission
- `question` → Many answers to one Question

**Constraints:**
- `unique_together`: `(submission, question)` - One answer per question per submission

**Indexes:**
- `submission`
- `question`
- `(submission, question)` - Composite index

**Computed Properties:**
- `percentage_score`: (score / max_score) * 100

---

## 📐 Entity Relationship Diagram

```
┌─────────────────┐
│      User       │
│  (Custom Auth)  │
└────────┬────────┘
         │
         │ instructor (FK)
         │
         ▼
┌─────────────────┐         ┌─────────────────┐
│     Course      │────────▶│      Exam       │
│                 │ 1:N     │                 │
└─────────────────┘         └────────┬────────┘
                                     │
                                     │ exam (FK)
                                     │
                            ┌────────┴────────┐
                            │                 │
                            ▼                 ▼
                   ┌─────────────────┐ ┌─────────────────┐
                   │    Question     │ │   Submission    │
                   │                 │ │                 │
                   └────────┬────────┘ └────────┬────────┘
                            │                   │
                            │                   │ submission (FK)
                            │                   │
                            │         ┌─────────┘
                            │         │
                            ▼         ▼
                         ┌─────────────────┐
                         │     Answer      │
                         │                 │
                         └─────────────────┘

┌─────────────────┐
│      User       │
│                 │
└────────┬────────┘
         │
         │ user (FK)
         │
         ▼
┌─────────────────┐
│   Submission    │
│                 │
└─────────────────┘
```

---

## 🔗 Detailed Relationships

### One-to-Many Relationships:

1. **User → Course** (as instructor)
   - One instructor can teach many courses
   - Each course has one instructor
   - `Course.instructor` → `User.courses_taught`

2. **Course → Exam**
   - One course can have many exams
   - Each exam belongs to one course
   - `Exam.course` → `Course.exams`

3. **Exam → Question**
   - One exam can have many questions
   - Each question belongs to one exam
   - `Question.exam` → `Exam.questions`

4. **Exam → Submission**
   - One exam can have many submissions
   - Each submission is for one exam
   - `Submission.exam` → `Exam.submissions`

5. **User → Submission** (as student)
   - One student can make many submissions
   - Each submission belongs to one student
   - `Submission.user` → `User.submissions`

6. **Submission → Answer**
   - One submission can have many answers
   - Each answer belongs to one submission
   - `Answer.submission` → `Submission.answers`

7. **Question → Answer**
   - One question can have many answers (from different students)
   - Each answer corresponds to one question
   - `Answer.question` → `Question.answers`

---

## 🔐 Database Constraints

### Unique Constraints:
- `User.email` - Each email must be unique
- `Course.code` - Each course code must be unique
- `(Submission.user, Submission.exam)` - One submission per user per exam
- `(Answer.submission, Answer.question)` - One answer per question per submission

### Foreign Key Constraints:
- All foreign keys use `CASCADE` on delete to maintain referential integrity
- Deleting a course deletes all associated exams
- Deleting an exam deletes all questions and submissions
- Deleting a submission deletes all associated answers

### Check Constraints:
- `Question.points` >= 0
- `Answer.score` >= 0
- `Submission.total_score` >= 0

---

## 📊 Index Strategy

### Single-Column Indexes:
- Primary keys (automatic)
- Foreign keys (automatic in most databases)
- `User.email`, `User.role`
- `Course.code`, `Course.is_published`
- `Exam.is_published`, `Exam.start_time`, `Exam.end_time`
- `Question.question_type`, `Question.order`
- `Submission.status`, `Submission.submitted_at`

### Composite Indexes:
- `(Course.instructor, Course.is_published)` - For instructor's published courses
- `(Exam.course, Exam.is_published)` - For course's published exams
- `(Question.exam, Question.order)` - For ordered questions in an exam
- `(Submission.user, Submission.exam)` - For unique constraint and queries
- `(Submission.exam, Submission.status)` - For exam submissions by status
- `(Answer.submission, Answer.question)` - For unique constraint and queries

---

## 🎯 Query Optimization

The schema is optimized for common query patterns:

1. **List student's submissions:**
   ```sql
   WHERE user_id = ? ORDER BY submitted_at DESC
   -- Uses: (user) index
   ```

2. **Get exam details with questions:**
   ```sql
   SELECT * FROM exams WHERE id = ?
   SELECT * FROM questions WHERE exam_id = ? ORDER BY order
   -- Uses: (exam, order) composite index
   ```

3. **Find active exams for a course:**
   ```sql
   WHERE course_id = ? AND is_published = true 
   AND start_time <= NOW() AND end_time >= NOW()
   -- Uses: (course, is_published) and time indexes
   ```

4. **Get submission with answers:**
   ```sql
   SELECT * FROM submissions WHERE id = ?
   SELECT * FROM answers WHERE submission_id = ?
   -- Uses: (submission) index
   ```

---

## 📝 Notes

- All timestamps use UTC
- JSON fields allow flexible data storage without schema changes
- The `metadata` fields enable feature additions without migrations
- Soft deletes are not implemented (use `is_active` flags instead)
- The schema supports ~10,000 concurrent users with proper database tuning

---

## 🚀 Database Choices

### Development:
- **SQLite** - Simple, no setup required
- Good for local development and testing

### Production:
- **PostgreSQL** - Recommended
- Better JSON support
- Advanced indexing
- Better concurrent write performance
- Supports millions of records

---

## 📚 Related Documentation

- [README.md](./README.md) - Project overview and setup
- Model definitions in respective apps:
  - `users/models.py`
  - `courses/models.py`
  - `exams/models.py`
  - `submissions/models.py`
