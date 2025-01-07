from bottle import Bottle, run, request, response
from environment.rl_environment import Environment
from database.db_manager import DatabaseManager

app = Bottle()
db_manager = DatabaseManager("environment_data.db")


@app.route('/environment/create', method='POST')
def create_environment():
    data = request.json
    board_size = data.get('board_size', (10, 10))
    obstacle_count = data.get('obstacle_count', 5)
    start = data.get('start', (0, 0))
    end = data.get('end', (board_size[0] - 1, board_size[1] - 1))

    # Create the environment
    env = Environment(board_size, obstacle_count, start, end)
    db_manager.store_environment({
        "board_size": board_size,
        "obstacle_count": obstacle_count,
        "start": start,
        "end": end
    })

    return {"status": "success", "message": "Environment created"}


@app.route('/environment/test_run', method='POST')
def run_test_simulation():
    env = Environment()
    # Run a simple test simulation (replace this with actual agent simulation if needed)
    result = {"status": "success", "data": "Test simulation complete"}
    return result


if __name__ == "__main__":
    run(app, host='localhost', port=8080)
