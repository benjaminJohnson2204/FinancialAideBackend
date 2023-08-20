# Financial Aide Back End

This is the back end for a budgeting website tool I built. It is hosted on Vercel at https://financial-aide-backend.vercel.app/.

There is a separate front end repository, hosted on a separate domain. Its code can be found at https://github.com/benjaminJohnson2204/financial-aide-frontend.

## Tech Stack

I used Django, Django REST Framework, DRF Spectacular, and Postgres for the back end.

## How to Run

1. Acquire the necessary environment variables. See `.env.example` for an example environment variables file.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the development server: `python manage.py runserver`

## Major Features

See https://github.com/benjaminJohnson2204/financial-aide-frontend#major-features for a usage-oriented description of the project's features.

## Apps

I divided the project into 4 apps to handle different functionality:
- **budgets**: Handles the tables of budgets, budget catgories (which are read-only to users), and budget category relations (the relations a user creates to link their budget to categories).
- **expenses**: Handles the table of expenses, and for comparing planned vs. actual spending
- **users**: Handles authentication: logging in, creating an account, logging out, and retrieving the current user
- **utils**: Utility functionality common to one or more other apps. I only ended up using it for an empty serializer class, and the budget frequency choices enum. 

## Authentication

I used Django's ModelBackend (i.e. storing users in the database) and session authentication. Session authentication was a bit tricky to get
to work with separate front end and back end domains, because the back end's login and register responses set session and CSRF cookies on the **back end's** domain, so
they are still sent with requests but are not visible to client-side JS. I made a custom middleware (`users.middleware.ShowCsrfTokenMiddleware`) to solve this problem: when a user logs in or signs up,
this middlware exposes the `Set-Cookie:csrftoken=<csrftoken>` header to the client so the JS can set the cooke on the front end's domain and later read it for CSRF protection. 

## Database

I used a SQLite (Django starter project's default) database for local development, and Postgres for production deployment.
The production database is hosted on ElephantSQL.

## Tests

I wrote unit tests for each app to verify the functionality of my code. I mainly tested hitting the API endpoints and ensuring the response it what is expected
(status code, response content, effects or lack thereof on DB state). I used Django's built-in testing framework, built on the Python `unittest` module, for my tests. 
The tests can be found in a `tests.py` file within each of my apps (e.g. `budgets/tests.py`). You can run them with `python manage.py test`.

## Documentation

I documented my API using DRF Spectacular, a Django REST Framework package that allows you to generate an OpenAPI specification from your views (path, method, request & response content, etc). You can them convert that specification to a Swagger UI page. 

My documentation is hosted on the `/docs` path: https://financial-aide-backend.vercel.app/docs/. To generate a documentation file, run `python manage.py spectacular --file schema.yaml`. This will create a `schema.yaml` file with the API specification. The 
`schema.yaml` file is used to display documentation on the `/docs` path. 

I also used this schema specification to generate a client for my front end using the Swagger editor at https://editor.swagger.io/.
