# Recipe Manager

A simple, self-hosted web application to manage your personal recipes. Built with FastAPI, Jinja2, and Bootstrap, and containerized with Docker for easy deployment.

## Features

*   **View Recipes:** Browse all your recipes in a clean, responsive grid.
*   **Create & Edit:** A dynamic form allows you to easily add new recipes or edit existing ones, including ingredients, instructions, and notes.
*   **Tagging:** Organize your recipes with tags and filter by them.
*   **Search:** Quickly find recipes by name.
*   **Photo Uploads:** Add a photo to each recipe.
*   **Responsive Design:** Works on both desktop and mobile browsers.

## Technology Stack

*   **Backend:** Python 3.11 with FastAPI
*   **Frontend:** Jinja2 Templates with Bootstrap 5
*   **Database:** MySQL 8.0
*   **Deployment:** Docker & Docker Compose

## Project Structure

```
recipe-manager/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── README.md
└── app/
    ├── main.py
    ├── models.py
    ├── schemas.py
    ├── crud.py
    ├── database.py
    ├── static/
    │   ├── placeholder.jpg
    │   └── uploads/
    └── templates/
        ├── base.html
        ├── index.html
        ├── recipe_detail.html
        ├── recipe_form.html
        └── components/
            └── recipe_card.html
```

## Setup and Installation

### Prerequisites

*   Docker
*   Docker Compose

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd recipe-manager
    ```

2.  **Build and run the containers:**
    ```bash
    docker-compose up --build -d
    ```
    This command will build the FastAPI application image and start the `app` and `db` services in detached mode.

3.  **Access the application:**
    Open your web browser and navigate to `http://localhost:8000`.

The application will be running, and any changes you make to the source code in the `app/` directory will trigger an automatic reload of the server.

## Database Backup

To create a manual backup of your MySQL database, you can run the following command from the `recipe-manager` directory. This will dump the contents of the `recipe_db` database into a `backup.sql` file in your current directory.

```bash
docker-compose exec db mysqldump -u root -p'rootpassword' recipe_db > backup.sql