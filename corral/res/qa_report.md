# {{pipeline_setup.name}} Quality Report

- **Created at:** {{report.created_at}}
- **Corral Version:** {{core.get_version()}}


## 1. Summary

- **Tests Success:** `{{ "Yes" if report.is_test_sucess else "No" }}`
- **Tests Ran:** `{{ report.test_runs }}`
- **Processors:** `{{ report.processors_number }}`
- **Coverage:** `{{ "{:.2f}".format(report.coverage_line_rate * 100) }}%`
- **Maintainability & Style Errors:** `{{ report.style_errors }}`

<!-- -->

- **QA Index:** `{{ "{0:.2f}%".format( report.qai * 100) }}`
- **QA Qualification:** `{{ report.cualification }}`

{% if explain_qai %}
### 1.1 About The Corral Quality Assurance Index (QAI)

```
{{ qai_doc }}
```

**Current Value of Tau:**: `{{ "{:.2f}".format(tau) }}` per file


### 1.2 About The Qualification

The Corral qualification is a quantitave scale based on QAI

{% for lowlimit, c in cualifications %}
- QAI >= {{ "{:.2f}".format(lowlimit) }}% -- `{{ c }}`
{%- endfor %}

{%- endif %}


{% if full_output %}
## 2. Full Output

### 2.1 Tests
```
{{ report.test_report }}
```
---

### 2.2 Coverage
```
{{ report.coverage_report }}
```
---

### 2.3 MAINTAINABILITY & STYLE
```
{{ report.style_report }}
```
{%- endif %}


