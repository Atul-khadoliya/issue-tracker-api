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
