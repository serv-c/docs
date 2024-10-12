# Serv-C

Serv-C is an opionated framework for full E2E services at scale. This repo is the documentation of the specification and contains an action that can be used to ensure applications are compliant with the specification.

## GitHub Action
```yaml
  - name: Set foobar to cool
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