from yaml import loader
import click
import yaml
import os

from jinja2 import Environment, FileSystemLoader

TEMPLATE_FOLDER = os.path.dirname(os.path.realpath(__file__))
TESTBED_YAML = 'testbed.yaml'

def render_template(template, sessions):
    file_loader = FileSystemLoader(TEMPLATE_FOLDER)
    env = Environment(loader=file_loader)
    env.add_extension('jinja2.ext.do')
    template = env.get_template(template)
    return template.render(sessions=sessions)

def generate(testbed_file):
    inventory = load_inventory(testbed_file)
    labs = {}

    def lab_store(lab_name):
        if lab_name in labs.keys():
            return labs[lab_name]
        
        labs[lab_name] = load_lab(os.path.join(os.path.dirname(testbed_file), testbed['inventory']))
        return labs[lab_name]

    sessions = []
    for testbed in inventory:
        duts, ptfs = lab_store(testbed['inventory'])

        # folder
        folder = os.path.join(
            'lab',
            testbed['topo'],
            testbed['testbed_name']).replace('\\', '/')

        # others
        for dut in testbed['duts']:
            if dut not in duts.keys():
                continue

            session = {}
            session['folder'] = folder
            session['session_name'] = dut
            session['host_name'] = duts[dut]
            session['protocol'] = 'SSH2'
            session['port'] = 22
            session['username'] = 'admin'
            session['testbed'] = testbed['testbed_name']
            session['topo'] = testbed['topo']
            session['type'] = 'dut'
            sessions.append(session)
        
        ptf = testbed['ptf']
        if ptf in ptfs.keys():
            session = {}
            session['folder'] = folder
            session['session_name'] = ptf
            session['host_name'] = ptfs[ptf]
            session['protocol'] = 'SSH2'
            session['port'] = 22
            session['username'] = 'root'
            session['testbed'] = testbed['testbed_name']
            session['topo'] = testbed['topo']
            session['type'] = 'ptf'
            sessions.append(session)
    return sessions

def load_inventory(inventory_file):
    with open(inventory_file, 'r') as file:
        inventory = yaml.safe_load(file)

    testbeds = []
    for item in inventory:
        if 'conf-name' in item:
            testbed = { 'testbed_name': item['conf-name'] }

            add_if_exists(testbed, 'group', item, 'group-name')
            add_if_exists(testbed, 'topo', item, 'topo')
            add_if_exists(testbed, 'server', item, 'server')
            add_if_exists(testbed, 'owner', item, 'comment')
            add_if_exists(testbed, 'ptf', item, 'ptf')
            add_if_exists(testbed, 'duts', item, 'dut')
            add_if_exists(testbed, 'inventory', item, 'inv_name')

            if 'inventory' in testbed.keys():
                testbeds.append(testbed)

    return testbeds

def load_lab(lab_file):
    if not os.path.isfile(lab_file):
        return {}, {}

    with open(lab_file, 'r') as file:
        lab = yaml.safe_load(file)

    ptfs = load_ptfs(lab)
    duts = load_duts(lab)

    return duts, ptfs

def load_ptfs(lab):
    ptfs = {}
    if 'all' not in lab.keys() or 'children' not in lab['all'].keys():
        return ptfs

    items = lab['all']['children']['ptf']

    # get hosts
    hosts = items['hosts']
    for key, val in hosts.items():
        add_if_exists(ptfs, key, val, 'ansible_host')
    
    return ptfs

def load_duts(lab):
    duts = {}
    if 'sonic' not in lab.keys() or 'children' not in lab['sonic'].keys():
        return duts

    children = lab['sonic']['children']
    for key, _ in children.items():
        if key not in lab.keys():
            continue

        child = lab[key]
        hosts = child['hosts']
        for key, val in hosts.items():
            add_if_exists(duts, key, val, 'ansible_host')
    
    return duts

def add_if_exists(obj, field, item, key):
    if key in item.keys():
        obj[field] = item[key]

@click.group()
def cli():
    pass

@cli.command()
@click.option('--template', default='sample.securecrt.j2', help='A jinja template path, default value is sample.securecrt.j2')
@click.argument('testbed_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.File('w'))
def dump(template, testbed_file, output_file):
    """Dump ssh sessions based on a template

    TESTBED_FILE is testbed yaml file path\n
    OUTPUT_FILE is output file path
    """
    sessions = generate(testbed_file)
    output = render_template(template, sessions)
    output_file.write(output)
    click.echo('Successfully dump to: {}'.format(output_file.name))

if __name__ == "__main__":
    cli()
