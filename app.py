from flask import Flask, request, redirect, send_from_directory, render_template
import logging
import os
import antiplagiat
from parsing import parsing

app = Flask(__name__)

# create logger instance
logger = logging.getLogger(__name__)
logger.setLevel('INFO')
inputs = ["Type your site link here"]
outputs = ['']
execute_counters = [0]
current_execute_count = 0
params = ['crc32', 2, False]


@app.route('/favicon.svg')
def favicon():
    """Handles browser's request for favicon"""
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'noun_Search_1221934.svg'
    )


@app.route('/submit', methods=['POST'])
def submit():
    """Changes parameters of anitiplagiat algorithm"""
    global params
    params[0] = request.form.get('hash')
    params[1] = request.form.get('len')
    params[2] = request.form.get('rus')
    return redirect('/')


@app.route('/execute_cell/<cell_id>', methods=['POST'])
def execute(cell_id=None):
    """Gets piece of code from cell_id and executes it"""
    try:
        cell_id = int(cell_id)
    except ValueError as e:
        logger.warning(e)
        return redirect('/')

    global current_execute_count
    try:
        current_execute_count += 1
        execute_counters[cell_id] = current_execute_count

        inputs[cell_id] = request.form['input{}'.format(cell_id)]
        texts = parsing(inputs[cell_id].split())
        result = antiplagiat.compare(texts=texts, algorithm=params[0],
                                     shingle_length=int(params[1]), flag=params[2])
    except BaseException as e:
        # anything could happen inside, even `exit()` call
        result = [str(e)]

    outputs[cell_id] = result
    return redirect('/')


@app.route('/', methods=['GET'])
def get():
    return render_template(
        'web_antiplagiat.html',
        cells=zip(range(len(inputs)), inputs, outputs, execute_counters),
        params=params)


@app.route('/add_link', methods=['POST', 'GET'])
def add_link():
    """Appends empty cell data to the end"""
    inputs.append('')
    outputs.append('')
    execute_counters.append(0)
    return redirect('/')


@app.route('/remove_cell/<cell_id>', methods=['POST'])
def remove_cell(cell_id=0):
    """Removes a cell by number"""
    try:
        cell_id = int(cell_id)
        if len(inputs) < 2:
            raise ValueError('Cannot remove the last cell')
        if cell_id < 0 or cell_id >= len(inputs):
            raise ValueError('Bad cell id')
    except ValueError as e:
        # do not change internal info
        logger.warning(e)
        return redirect('/')

    # remove related data
    inputs.pop(cell_id)
    outputs.pop(cell_id)
    execute_counters.pop(cell_id)
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
