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

### Step 2: Create a Virtual Environment

```bash
python -m venv venv


