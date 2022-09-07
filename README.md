# superset-ext

Meltano Superset utility extension

### example meltano.yml

Note: this example uses a name of `ext_superset` instead of `superset` to avoid conflicts and special handling for the
existing `superset` plugin.

```yaml
utilities:
  - name: ext_superset
    namespace: superset
    pip_url: apache-superset==2.0.0 flask==2.0.3 werkzeug==2.0.3 jinja2==3.0.1 git+https://github.com/meltano/superset-ext.git@feat/init-extension-take2
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
      create-admin:
        args: fab create-admin
        executable: superset
      ui:
        args: invoke run --port 8088 --host 127.0.0.1
    config:
      ROW_LIMIT: 42
      SQLALCHEMY_DATABASE_URI: sqlite:///$MELTANO_PROJECT_ROOT/superset/superset.db
      SUPERSET_WEBSERVER_PORT: 8088
      SUPERSET_CONFIG_PATH: $MELTANO_PROJECT_ROOT/superset/superset_config.py
```

## installation

```shell
# Install the extension
meltano install utility superset_ext

# Setup a superset secret key
meltano config superset_ext set SECRET_KEY $(openssl rand -base64 42)

# explicitly create the superset config python file and call `superset db upgrade`
meltano invoke superset_ext:initialize

# verify that superset can be called via the extensions invoker
meltano invoke superset_ext version
# see what other commands are available
meltano invoke superset_ext --help

# add a superset admin using supersets `fab create-admin` command
meltano invoke superset_ext:create-admin

# start the superset dev server
meltano invoke superset_ext:ui
```
