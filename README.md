# Serv-C

Serv-C is an opionated framework for full E2E services at scale. This repo is the documentation of the specification and contains an action that can be used to ensure applications are compliant with the specification.

## GitHub Action
```yaml
name: 'Serv-C Unit Test'
on:
  - push

jobs:
  servc:
    runs-on: ubuntu-latest

    services:
      rabbitmq:
        image: rabbitmq:3
        env:
          RABBITMQ_DEFAULT_USER: guest
          RABBITMQ_DEFAULT_PASS: guest
        ports:
          - 5672/tcp

      redis:
        image: redis
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5                    
        ports:
          - 6379/tcp

    steps:
      - name: Run Servc Tests
        uses: serv-c/docs@main
        with:
          # the dockerfile to be used for building the
          # application/library
          dockerfile: Dockerfile
          context: '.'

          # run a particular suite. Useful if the library
          # or application is geared towards a specific
          # set of functionalities.
          # suites:
          #     ''          all
          #     config      just configuration related
          #     service     microservice
          suite: ''

          # run a particular version of the spec
          # useful to check compliance against a specific
          # version. defaults to latest (main)
          version: 'main'
```