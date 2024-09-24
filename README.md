## Bysykkel demo

### Step 1

#### Prerequisites
- [Node.js and npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
  - Tested on node v18.20.2 and npm v10.5.0

#### Steps
1. Install dependencies:
    ```sh
    npm install
    ```

2. Start app:
    ```sh
    npm run dev
    ````

3. Go to http://localhost:5173 to see the list of stations and their bike availability

### Step 2

#### Prerequisites
- [Python 3.10 or higher](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/)
  - Tested on v1.8.3
- [Redis](https://redis.io/docs/latest/operate/oss_and_stack/install/install-redis/) running
  - We assume you're running it on port 6379, but if otherwise, simply pass the correct port [here](app.py#L11).

#### Steps
1. Install dependencies
    ```sh
    poetry install
    ```

2. Start web server:
    ```sh
    poetry run uvicorn --port 8000 app:app --reload
    ```

3. Give it a whirl by e.g. getting data about station 574 at http://localhost:8000/api/stations/574:
    ```sh
    curl http://localhost:8000/api/stations/574
    ```
    or fetch all stations with available bikes at http://localhost:8000/api/stations/available:
    ```sh
    curl http://localhost:8000/api/stations/available
    ```
