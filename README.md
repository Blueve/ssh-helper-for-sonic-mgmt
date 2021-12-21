# ssh-helper-for-sonic-mgmt
This is a tool for dumping ssh connections files for SecureCRT/openssh-client/...

## Dependency

To run the script, you need to install all below 3rd party packages.
```bash
pip3 install pyyaml
pip3 install jinja2
pip3 install click
```

## Quick Start

Use following command to generate SecureCRT sessions data, then follow [Importing SecureCRT Sessions from a Data File](https://www.vandyke.com/support/tips/importsessions.html) to import them to your SecureCRT
```bash
python export_sessions.py dump testbed.yaml sessions.csv
```

Use following command to generate ssh short cut configuration, then append them to your own ssh configuration
```bash
python export_sessions.py dump testbed.yaml sessions.config --template sample.ssh.j2
```

## Customization

Feel free to customize the template for you favored terminal tool.
The script will pass following object to jinja template:

```json
[{
    'folder': < default folder was combined by lab/{topo}/{testbed} >,
    'session_name': < default session_name is hostname >,
    'host_name': < IP address of host >,
    'protocol': < connection protocol, default value is SSH2 >,
    'port': < connection port, default value is 22 >,
    'username': < connection username >,
    'topo': < the topology of testbed >,
    'testbed': < the testbed name >,
    'type': < dut|ptf >,
}, ...]
```

The sample `sample.securecrt.j2` is designed for SecureCRT, it use the default folder formatter we provided. You can also add your own logic before generate the csv file, for example, we can simplify the folder structure by doing this:

```jinja
## Replace
## {{ session['folder'] }}

testbeds/{{ session['testbed']}}
```
