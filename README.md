# superset-ext

Meltano Superset utility extension

### example meltano.yml

Note: this example uses a name of `ext_superset` instead of `superset` to avoid conflicts and special handling for the
existing `superset` plugin.

```yaml
utilities:
  - name: ext_superset
    namespace: superset
    pip_url: apache-superset==2.0.0 flask==2.0.3 werkzeug==2.0.3 jinja2==3.0.1 wtforms==2.3.3 git+https://github.com/meltano/superset-ext.git@main
    executable: superset_invoker
    commands:
      describe:
        executable: superset_extension
        args: describe
      initialize:
        executable: superset_extension
        args: initialize
      invoke:
        executable: superset_extension
        args: invoke
      create_admin:
        args: create_admin
        executable: superset_extension
      ui:
        args: invoke run --port 8088 --host 127.0.0.1
    config:
      ROW_LIMIT: 42
      SQLALCHEMY_DATABASE_URI: sqlite:///$MELTANO_PROJECT_ROOT/.meltano/utilities/superset/superset.db
      SUPERSET_WEBSERVER_PORT: 8088
      SUPERSET_CONFIG_PATH: $MELTANO_PROJECT_ROOT/superset/superset_config.py
```

## installation

Note that the installation of Superset 2.0 from pip can take a bit longer than other extensions (~10 minutes).

```bash

```shell
# Install the extension
meltano install utility superset_ext

# Setup a superset secret key
meltano config superset_ext set SECRET_KEY $(openssl rand -base64 42)

# explicitly create the superset config python file and call `superset db upgrade`
meltano invoke superset_ext:initialize

# add a superset admin using prompting for required values
meltano invoke superset_ext:create_admin
# add a superset admin passing in required values via flags
meltano invoke superset_ext:create_admin --username=admin --firstname=admin --lastname=admin --
email=admin@admin --password=password

# verify that superset can be called via the extensions invoker
meltano invoke superset_ext version
# see what other commands are available
meltano invoke superset_ext --help

# start the superset dev server
meltano invoke superset_ext:ui
```
