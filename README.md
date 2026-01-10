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


