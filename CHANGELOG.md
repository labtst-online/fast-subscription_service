# CHANGELOG


## v0.1.1 (2025-05-09)

### Bug Fixes

- Refactor CD workflow to use workflow_run for CI success confirmation and streamline release
  process
  ([`c5962e4`](https://github.com/fotapol/fastboosty-subscription_service/commit/c5962e40aea95cf88cc2f17cea2088dd1637d2b1))

- Update Dockerfile and .dockerignore for improved dependency management and build efficiency
  ([`c85bf53`](https://github.com/fotapol/fastboosty-subscription_service/commit/c85bf53fbc11bb5f765dfaf03841f57e5a015e1a))

- Update semantic release configuration for release management in pyproject.toml
  ([`665cc84`](https://github.com/fotapol/fastboosty-subscription_service/commit/665cc84284e027c9c4490ba92be8d765848b6e3c))

### Chores

- Styling code using ruff formater
  ([`d497ad1`](https://github.com/fotapol/fastboosty-subscription_service/commit/d497ad1090fcc89e6a64d2eab1a386fb72b792cf))


## v0.1.0 (2025-05-08)

### Bug Fixes

- Remove AUTH_SERVICE_URL from config and .env.sample
  ([`58e1814`](https://github.com/fotapol/fastboosty-subscription_service/commit/58e1814930f56202634ddabba28300c60a14040f))

- **subscription**: Correct spelling of 'pending' and update table names in models
  ([`f8ef4d2`](https://github.com/fotapol/fastboosty-subscription_service/commit/f8ef4d2b20f8e249bc4b22f8b79f804876c62cc2))

### Features

- Add auth-lib dependency for authentication handling
  ([`c82feaf`](https://github.com/fotapol/fastboosty-subscription_service/commit/c82feafe0e3eb387452b1805dc718cc6910b0ded))

- Add CI workflow for testing and formatting checks
  ([`aedfa98`](https://github.com/fotapol/fastboosty-subscription_service/commit/aedfa989b28bb75c15651a01905c5ef269fddfb3))

- Add Continuous Delivery workflow and update Continuous Integration workflow
  ([`2fbed9e`](https://github.com/fotapol/fastboosty-subscription_service/commit/2fbed9e303b381131b4650fb707b702860f51e92))

- Add initial .dockerignore file to exclude Python cache
  ([`c9b52ff`](https://github.com/fotapol/fastboosty-subscription_service/commit/c9b52ff5b6c0e5645815ee81aaf5261ab6348bcf))

- Add python-semantic-release package. Update main.py.
  ([`a2b5a17`](https://github.com/fotapol/fastboosty-subscription_service/commit/a2b5a1702238aad1d11539ccad62825c1c1238ce))

- Remove deprecated import of CurrentUserUUID from dependencies and add new import from new package
  ([`245656e`](https://github.com/fotapol/fastboosty-subscription_service/commit/245656e358cdcd3bb6aa2dfd4e7e2bc35e8f3fdc))

- Update auth-lib version to latest
  ([`5c3a423`](https://github.com/fotapol/fastboosty-subscription_service/commit/5c3a4230174b6ebc475301962583989a93569920))

- Update CI/CD workflows to enhance dependency management and permissions
  ([`639ca89`](https://github.com/fotapol/fastboosty-subscription_service/commit/639ca8992960fe96f49aadcba3d3001cb40e3a31))

- Update Python version to 3.13 in the Dockerfile. Update dependencies
  ([`a1f3715`](https://github.com/fotapol/fastboosty-subscription_service/commit/a1f37159a5c148d3bab62534d6456a6ad29ac67f))

- **subscription**: Add Alembic configuration and migration scripts for subscription service
  ([`0de09b0`](https://github.com/fotapol/fastboosty-subscription_service/commit/0de09b08c177a3fcd3cab474ad4d99418f823658))

- **subscription**: Add currency field to Tier model and update related schemas. Add model for Kafka
  ([`1972bec`](https://github.com/fotapol/fastboosty-subscription_service/commit/1972becd6c91385718f85812674e7146be1eef89))

- **subscription**: Add dependency for user authentication via JWT token
  ([`6426c78`](https://github.com/fotapol/fastboosty-subscription_service/commit/6426c78f1748179f68096b6ec40cc2d00f845a53))

- **subscription**: Add Dockerfile and .dockerignore for containerization
  ([`c14f5a7`](https://github.com/fotapol/fastboosty-subscription_service/commit/c14f5a7db82c49d4908a043d009a8685bce31649))

- **subscription**: Add entrypoint script for database readiness and migrations. Rename tier route
  and update health check service name. Update configuration for ruff
  ([`807a1da`](https://github.com/fotapol/fastboosty-subscription_service/commit/807a1da52c66cfb2744ea663ceaff7040130071a))

- **subscription**: Add PAYMENT_SERVICE_URL to configuration and update .env.sample
  ([`8f0086e`](https://github.com/fotapol/fastboosty-subscription_service/commit/8f0086e31dcda7db9fe85adf932c06073eb517e4))

- **subscription**: Add PAYMENT_SERVICE_URL to configuration and update .env.sample
  ([`93a313c`](https://github.com/fotapol/fastboosty-subscription_service/commit/93a313cbb11821948e6cb13988d64be22bc779d7))

- **subscription**: Add pototypes of models and schemas for Subscription and Tier entities
  ([`6821ef7`](https://github.com/fotapol/fastboosty-subscription_service/commit/6821ef731f93bb0601d85f4d94a23392a856c44f))

- **subscription**: Add SubscriptionStatus enum for improved status management in Subscription model
  ([`4f8d853`](https://github.com/fotapol/fastboosty-subscription_service/commit/4f8d853c1a5ebd6820e83ec09df9aaa10df74ca7))

- **subscription**: Create prototypes of subscription and tier routes, implement main.py. Create
  outline of internal router for checking access.
  ([`49f4836`](https://github.com/fotapol/fastboosty-subscription_service/commit/49f48361d9cc778fa0683dcdff9a9567e9d05673))

- **subscription**: Implement access check logic in internal router
  ([`676ad1a`](https://github.com/fotapol/fastboosty-subscription_service/commit/676ad1a8845a1bc737aa5a6a3f3704596c831f8f))

- **subscription**: Implement CRUD operations for Tier entity with error handling and logging
  ([`a1eeef8`](https://github.com/fotapol/fastboosty-subscription_service/commit/a1eeef88b22ea15991cefafbb372536a7ec85501))

- **subscription**: Initialize subscription service with core files, configuration, and database
  setup
  ([`c944fdf`](https://github.com/fotapol/fastboosty-subscription_service/commit/c944fdf0845c798a762662e3e8fae5bb923fdc53))

- **subscription**: Integrate Kafka for payment event handling and subscription management
  ([`b8e1ed4`](https://github.com/fotapol/fastboosty-subscription_service/commit/b8e1ed41d934af05bc2594fe3b61e171b117046e))

- **subscription**: Integrate payment service call in subscription creation and update Kafka
  consumer initialization
  ([`c011edb`](https://github.com/fotapol/fastboosty-subscription_service/commit/c011edb62334c6c189b6edd64c2fee0bb2666f26))

- **subscription**: Realize subscription and tier routers.
  ([`37909cf`](https://github.com/fotapol/fastboosty-subscription_service/commit/37909cf5182ab66dd321dfa100bccd216031658b))

- **subscription**: Update Alembic environment to include Subscription and Tier models for
  migrations
  ([`6fb7bc0`](https://github.com/fotapol/fastboosty-subscription_service/commit/6fb7bc03734833a9a599706c21e076499b6e386d))

- **subscription**: Update models for subscription and tiers. Update model for metadata
  ([`774d69d`](https://github.com/fotapol/fastboosty-subscription_service/commit/774d69d89c6121debb82cf578e30bd77448fde3c))

- **subscription**: Update schemas to use UUID and datetime types for better data integrity
  ([`0898842`](https://github.com/fotapol/fastboosty-subscription_service/commit/0898842b6c4565f3ca62c168d63a49d265c99566))

- **subscription**: Update service title and change port configuration
  ([`b096cdc`](https://github.com/fotapol/fastboosty-subscription_service/commit/b096cdc6ae952a8ca7733cab5a93f72e15f88625))

### Refactoring

- Clean up extra comments
  ([`adb5335`](https://github.com/fotapol/fastboosty-subscription_service/commit/adb5335b20971a17b4bffd3593160384026f7d3d))

- Code styling using ruff formater
  ([`43e4f76`](https://github.com/fotapol/fastboosty-subscription_service/commit/43e4f7661bc67d798fcb8f54623ac3297cd52089))

- **subscription**: Simplify access check and improve parameter handling in subscription routes. Fix
  bugs
  ([`0029cd6`](https://github.com/fotapol/fastboosty-subscription_service/commit/0029cd670216233e7977c0847683f5f9ec54602d))
