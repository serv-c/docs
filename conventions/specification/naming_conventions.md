# Naming Conventions

```
repository name: svc-[dns-compliant-name]
artifact name: servc/svc-[dns-compliant-name]
topic/route: svc-[dns-compliant-name]
event route:
  svc.event.[dns-compliant-instance].[verb]
  svc.event.[dns-compliant-category].[verb]
```

example:

```
repository name: svc-deluge
artifact name: servc/svc-deluge
topic/route: svc-deluge
event route:
  svc.event.deluge.completed-task
  svc.event.dl.completed-task
```
