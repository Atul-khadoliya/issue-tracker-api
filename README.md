 ## Project Overview

This project is a backend **Issue Tracker API** built using **Django REST Framework** and **PostgreSQL**.

The system allows teams to manage issues with support for:
- Safe concurrent updates using optimistic locking
- Comments and labels on issues
- Transactional bulk operations
- CSV-based issue import with partial success handling
- Aggregated reporting endpoints
- A derived issue timeline (bonus feature)

The API is designed to follow clean REST principles, handle concurrency correctly, and prioritize data consistency and clarity over unnecessary complexity.

## Tech Stack Used

### Backend
- **Python 3**
- **Django** – core web framework
- **Django REST Framework (DRF)** – building RESTful APIs

### Database
- **PostgreSQL** – primary relational database used in production

### Testing
- **pytest**
- **pytest-django** – Django integration for pytest

### Other Tools & Libraries
- **Django ORM** – database interactions and aggregations
- **Transaction management (`transaction.atomic`)** – ensuring data consistency
- **Pagination & filtering** – handled at the API layer using DRF
- **CSV parsing (`csv` module)** – for bulk issue import

The stack was chosen to prioritize reliability, correctness, and clarity, while remaining simple enough to reason about during development and review.


## How to Set Up the Project

### Step 1: Clone the Repository
```bash
git clone https://github.com/Atul-khadoliya/issue-tracker-api.git
cd issue-tracker-api
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```
### Step 3: Activate the Virtual Environment (Windows)
```bash
venv\Scripts\activate
```
### Step 4: Activate the Virtual Environment (macOS / Linux)
```bash
source venv/bin/activate
```
### Step 5: Install Project Dependencies
```bash
pip install -r requirements.txt
```
### Step 6: Configure the Database
```Open the file:
issue_tracker/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'issue_tracker_db',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```
### Step 7: Apply Database Migrations
```bash
python manage.py migrate
```
### Step 8: Start the Development Server
```bash
python manage.py runserver
 ```
### Step 9: Access the API in Browser
```
http://127.0.0.1:8000/
```

## API Overview

This section describes all available API endpoints, grouped by functionality.  
Each endpoint is explained logically to clarify its purpose and behavior.



### Issues

### Create an Issue
**POST /issues**

#### Request Body
json
{
  "title": "Issue title",
  "description": "Issue description",
  "status": "open",
  "assignee": 1
}
#### Data Handling & Logic

**Validation**
- `title` is required and must be non-empty  
- `status` must be one of the allowed status values  
- `assignee` must reference a valid user  
- Fields like `id`, `version`, `created_at`, and `updated_at` are read-only  

**Business Logic**
- A new issue is created  
- Every issue is initialized with a **version** field  
- The version field is used for optimistic concurrency control on updates  

**Database Operation**
- Inserts a new row into the `issues` table  
- Automatically sets timestamps and initial version  

**Response**
- Returns the created issue object including its initial version  


### List Issues
**GET /issues**

#### Query Parameters
json
{
  "status": "open",
  "assignee": 1,
  "page": 1
}

#### Data Handling & Logic

**Validation**
- All query parameters are optional  
- `status` must be one of the allowed status values if provided  
- `assignee` must reference a valid user if provided  
- `page` must be a valid pagination value  

**Business Logic**
- Retrieves issues from the system  
- Supports filtering by `status` and `assignee`  
- Results are ordered by creation time (newest first)  
- Pagination is applied to limit response size  

**Database Operation**
- Executes a filtered query on the `issues` table  
- Applies ordering and pagination at the database level  

**Response**
```json
{
  "count": 10,
  "next": "/issues?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "First issue",
      "description": "Issue description",
      "status": "open",
      "assignee": 1,
      "version": 1,
      "created_at": "2026-01-09T12:08:01Z",
      "updated_at": "2026-01-09T12:08:01Z"
    }
  ]
}
```

### Retrieve a Single Issue
**GET /issues/{id}**

#### Path Parameters
```json
{
  "id": 1
}
```
#### Data Handling & Logic

**Validation**
- `id` must reference an existing issue  
- Returns `404 Not Found` if the issue does not exist  

**Business Logic**
- Fetches the complete issue record  
- Includes related **comments** and **labels**  
- Read-only operation (no mutation)  

**Database Operation**
- Selects the issue by primary key  
- Performs related lookups for comments and labels  

**Response**
```json
{
  "id": 1,
  "title": "First issue",
  "description": "Issue description",
  "status": "open",
  "assignee": 1,
  "version": 1,
  "created_at": "2026-01-09T12:08:01Z",
  "updated_at": "2026-01-09T12:08:01Z",
  "comments": [
    {
      "id": 5,
      "body": "Needs investigation",
      "author": "atul",
      "created_at": "2026-01-09T14:10:00Z"
    }
  ],
  "labels": [
    {
      "id": 2,
      "name": "bug"
    }
  ]
}
```
### Update an Issue (Optimistic Concurrency)
**PATCH /issues/{id}**

#### Request Body
```json
{
  "title": "Updated issue title",
  "description": "Updated description",
  "status": "resolved",
  "assignee": 2,
  "version": 1
}
```
#### Data Handling & Logic

**Validation**
- `id` must reference an existing issue  
- `version` is required and must be an integer  
- Returns `400 Bad Request` if `version` is missing  
- Returns `404 Not Found` if the issue does not exist  

**Business Logic**
- Uses **optimistic concurrency control**  
- Compares the incoming `version` with the current version stored in the database  
- If versions do not match, the update is rejected  
- On success, updates only the provided fields and increments the version  

**Database Operation**
- Selects the issue by primary key  
- Updates issue fields inside a transaction  
- Increments the version and persists the changes  

**Response**
```json
{
  "id": 1,
  "title": "Updated issue title",
  "description": "Updated description",
  "status": "resolved",
  "assignee": 2,
  "version": 2,
  "created_at": "2026-01-09T12:08:01Z",
  "updated_at": "2026-01-10T09:30:00Z"
}
```
### Add a Comment to an Issue
**POST /issues/{id}/comments**

#### Request Body
```json
{
  "body": "This needs further investigation",
  "author": 1
}
```
#### Data Handling & Logic

**Validation**
- `id` must reference an existing issue  
- `body` is required and must be non-empty  
- `author` (provided because auth is not implemented in that case, comes in header) must reference a valid user  

**Business Logic**
- Associates the comment with the specified issue  
- Stores the comment as an immutable record  
- Does not modify the issue version or status  

**Database Operation**
- Inserts a new row into the `comments` table  
- Sets the foreign key reference to the issue  

**Response**
```json
{
  "id": 10,
  "body": "This needs further investigation",
  "author": "atul",
  "created_at": "2026-01-10T10:15:00Z"
}
```
### Replace Issue Labels
**PUT /issues/{id}/labels**

#### Request Body
```json
[
  { "name": "bug" },
  { "name": "urgent" }
]
```
#### Data Handling & Logic

**Validation**
- `id` must reference an existing issue  
- Request body must be a list of label objects  
- Each label `name` must be non-empty  

**Business Logic**
- Replaces all existing labels for the issue  
- Creates labels if they do not already exist  
- Operation is executed atomically to ensure consistency  

**Database Operation**
- Fetches the issue by primary key  
- Inserts new labels if required  
- Updates the issue–label relationship inside a transaction  

**Response**
```json
[
  { "id": 1, "name": "bug" },
  { "id": 2, "name": "urgent" }
]
```

### Bulk Update Issue Status
**PUT /issues/bulk-status**

#### Request Body
```json
[
  { "id": 1, "status": "resolved" },
  { "id": 2, "status": "closed" },
  .....
]
```
#### Data Handling & Logic

**Validation**
- Request body must be a list of objects  
- Each object must contain a valid `id` and `status`  
- `status` must be one of the allowed status values  
- Returns `400 Bad Request` if the payload structure is invalid  

**Business Logic**
- Updates the status of multiple issues in a single request  
- All updates are executed within a single transaction  
- If any update fails, the entire operation is rolled back  

**Database Operation**
- Fetches each issue by primary key  
- Updates the `status` and increments the `version` for each issue  
- Commits changes only if all updates succeed  

**Response**
```json
[
  {
    "id": 1,
    "title": "First issue",
    "status": "resolved",
    "version": 2
  },
  {
    "id": 2,
    "title": "Second issue",
    "status": "closed",
    "version": 3
  }
]
```
### Import Issues via CSV
**POST /issues/import**

#### Request Body
```text
multipart/form-data
file=<issues.csv>
```
#### CSV Format
```csv
title,description,status,assignee
Login bug,Error on login,open,1
UI glitch,Button misaligned,resolved,1
#### Data Handling & Logic
```
**Validation**
- A CSV file must be provided  
- File must have a `.csv` extension  
- CSV must contain headers: `title`, `description`, `status`, `assignee`  
- Each row is validated independently  

**Business Logic**
- Parses the CSV file row by row  
- Valid rows are inserted as new issues  
- Invalid rows are skipped without aborting the process  
- Supports partial success  

**Database Operation**
- Inserts a new row into the `issues` table for each valid CSV row  
- Does not wrap all inserts in a single transaction to allow partial success  

**Response**
```json
{
  "total_rows": 5,
  "created": 3,
  "failed": 2,
  "errors": [
    {
      "row": 2,
      "errors": {
        "status": ["Invalid status value"]
      }
    }
  ]
}
```

### Top Assignees Report
**GET /reports/top-assignees**

#### Data Handling & Logic

**Validation**
- No request parameters are required  
- Only issues with a non-null assignee are considered  

**Business Logic**
- Aggregates issues by assignee  
- Counts the number of issues assigned to each user  
- Orders the result in descending order of issue count  

**Database Operation**
- Executes a grouped aggregation query on the `issues` table  
- Uses `COUNT` to compute the number of issues per assignee  

**Response**
```json
[
  {
    "assignee": 1,
    "issue_count": 5
  },
  {
    "assignee": 2,
    "issue_count": 3
  }
]
```
### Average Resolution Time Report
**GET /reports/latency**

#### Data Handling & Logic

**Validation**
- No request parameters are required  
- Only issues with status `resolved` or `closed` are considered  

**Business Logic**
- Calculates the time difference between `created_at` and `updated_at`  
- Computes the average resolution time across all resolved/closed issues  

**Database Operation**
- Filters issues by terminal status  
- Uses a database-level expression to compute durations  
- Aggregates the average using `AVG`  

**Response**
```json
{
  "average_resolution_time": "16069.073806"
}
```
### Issue Timeline (Bonus)
**GET /issues/{id}/timeline**

#### Data Handling & Logic

**Validation**
- `id` must reference an existing issue  
- Returns `404 Not Found` if the issue does not exist  

**Business Logic**
- Builds a derived timeline of the issue’s history  
- Includes key events such as:
  - Issue creation
  - Status changes
  - Comment additions
  - Label updates
- Timeline is read-only and computed dynamically (no audit table)

**Database Operation**
- Fetches the issue by primary key  
- Retrieves related comments and labels  
- Does not persist timeline data; events are derived at request time  

**Response**
```json
[
  {
    "type": "created",
    "timestamp": "2026-01-09T12:08:01Z",
    "details": {
      "title": "First issue",
      "status": "open"
    }
  },
  {
    "type": "comment",
    "timestamp": "2026-01-09T14:10:00Z",
    "details": {
      "author": "atul",
      "body": "Needs investigation"
    }
  },
  {
    "type": "status_change",
    "timestamp": "2026-01-10T09:30:00Z",
    "details": {
      "status": "resolved"
    }
  }
]
```
## Testing

Testing focuses on validating the most critical and risk-prone parts of the system rather than exhaustively testing every endpoint.

### Testing Approach
- Automated tests are written using **pytest** and **pytest-django**
- Tests prioritize correctness of:
  - Optimistic concurrency control
  - Filtering and pagination logic
- Simpler CRUD endpoints are verified through manual testing

### Covered Test Scenarios
- Successful issue update with correct version
- Version conflict handling (`409 Conflict`) during concurrent updates
- Issue listing with pagination
- Issue filtering by status

### Running Tests
```bash
pytest
```

## Future Improvements

The current implementation focuses on core backend functionality and correctness.  
The following improvements can be added to enhance scalability, security, and usability:

### Authentication
- Add user authentication using JWT or session-based auth
- Restrict issue creation and updates to authenticated users

### Role-Based Access Control
- Introduce roles such as `admin`, `maintainer`, and `viewer`
- Restrict bulk operations and reports to privileged roles

### Async CSV Processing
- Move CSV import to a background job using Celery or Django-Q
- Prevent long-running requests for large CSV files
- Provide job status tracking for imports

### Audit Logs
- Persist issue history instead of deriving it dynamically
- Track changes such as status updates, assignee changes, and label modifications
- Useful for compliance and debugging in production systems
