# Changelog

All notable changes to this project will be documented in this file.

## [v0.1.2] - 2026-06-04
### Added
- Environment-driven configuration for Docker and runtime (`.env`, `application.yml.template`).
- `start.command` and `stop.command` updated to source `.env` and generate `application.yml` from template.
- `manual.txt` updated with `.env` usage and startup checklist.

### Changed
- Bumped documentation and metadata from `v0.1.1` to `v0.1.2`.
- `docker-compose.yml` now reads port mappings and container names from environment variables.

### Fixed
- Removed hardcoded ports and duplicated logic in startup scripts.

