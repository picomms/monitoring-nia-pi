# Grafana

Grafana is provisioned from files in the repo. The checked-in datasource and
dashboard JSON remain the source of truth.

## Datasource

`grafana/datasources/prometheus.yml` provisions the default Prometheus datasource:

```yaml
type: prometheus
access: proxy
url: http://prometheus:9090
uid: prometheus
isDefault: true
```

## Dashboard provisioning

`grafana/dashboards/dashboards.yml` loads every dashboard JSON in that directory into
the **NIA Monitoring** folder. `allowUiUpdates: true` lets an administrator
experiment in the UI, but it does not make the Grafana database authoritative:
the next file-provisioning update replaces conflicting UI changes.

## Editing a dashboard

1. Edit the JSON under `grafana/dashboards/` (stable human-readable `uid` values).
2. Wait up to 30 seconds for provisioning sync, or recreate the Grafana container:
   `docker compose up -d --force-recreate grafana`.
3. Refresh the browser.

If you prototype in the UI, export the resulting JSON and deliberately merge it
into the checked-in dashboard before relying on it.

Panels query PromQL against datasource uid `prometheus`. See
[Dashboards](../user/dashboards.md) for the current inventory (`cherry-host`).
