# Serv-C

Serv-C is an opionated framework for full E2E services at scale. This repo is the documentation of the specification and contains an action that can be used to ensure applications are compliant with the specification.

## Mandatory Library Startup Interfaces

**Test Method**
```
method: test
argument: str[]
response:
  false - if the argument does not meet type check.
  true - if the argument meeds the type check
```

## GitHub Action
```yaml
name: 'Serv-C Unit Test'
on:
  push:
  pull_request:

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
      #
      # ADD IN ALL YOUR SETUP HERE
      # eg: clone, install dependencies

      # step: Check out the document repository
      # description: This repo contains all the black
      #              box testing to assert that a library
      #              is serv-c compliant
      - name: Checkout Serv-C
        uses: actions/checkout@v4
        with:
          repository: serv-c/docs
          ref: main
          path: servc-docs
          sparse-checkout: |
            tests
            requirements.test.txt
            config/.placeholder
    
      # step: Install dependencies
      - name: Install Serv-C Dependencies
        run: pip install -r requirements.test.txt
        shell: bash
        working-directory: servc-docs
      
      # step: Run the Black Box Tests
      # description: runs the tests. The
      #              '**' can be modified to run a particular suite
      #              the START_SCRIPT is mandatory in order to startup
      #              the library implementation
      - name: Run Serv-C tests
        shell: bash
        working-directory: servc-docs
        env:
          START_SCRIPT: ${{ env.CURRENT_PATH }}/start.sh
          CACHE_URL: redis://redis
          BUS_URL: amqp://guest:guest@rabbitmq
        run: python -m unittest tests/**/*.py
```