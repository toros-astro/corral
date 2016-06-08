# {{pipeline_setup.name}} Documentation

- **Created at:** {{now}}
- **Corral Version:** {{core.get_version()}}

{{pipeline_setup.__doc__ or "`<EMPTY DOC>`"}}


{%- if models %}
## Models
{% for mdl in models %}
### Model **{{mdl.__name__}}**

- **Table:** `{{mdl.__table__}}`

{{ doc_formatter(mdl.__doc__ or "`<EMPTY DOC>`") }}

{% endfor %}
{%- endif %}


{%- if loader %}
## Loader:

- **Python Path** ``{{loader.retrieve_python_path()}}``

{{ doc_formatter(loader.__doc__ or "`<EMPTY DOC>`") }}
{% endif %}

{%- if steps %}
## Steps
{% for step in steps %}
### Step **{{step.__name__}}**

- **Python Path** ``{{step.retrieve_python_path()}}``

{{ doc_formatter(step.__doc__ or "`<EMPTY DOC>`") }}

{% endfor %}
{%- endif %}


{%- if alerts %}
## Alerts
{% for alert in alerts %}

### Alert **{{alert.__name__}}**

- **Python Path** ``{{alert.retrieve_python_path()}}``

{{ doc_formatter(alert.__doc__ or "`<EMPTY DOC>`") }}

{% endfor %}
{%- endif %}


# Command Line Interface

{{cli_help}}

