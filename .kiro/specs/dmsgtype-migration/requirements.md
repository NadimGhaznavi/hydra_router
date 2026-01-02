# Requirements Document

## Introduction

The Hydra Router system needs to complete the migration from `MessageType` to `DMsgType` constants. This migration involves updating import statements, class names, and ensuring consistent usage across the codebase. The current state has several inconsistencies that need to be resolved.

## Glossary

- **DMsgType**: The new constants class for message types, following the D-prefix naming convention
- **MessageType**: The old message type reference that needs to be replaced
- **Constants_Module**: The `hydra_router/constants/DMsgType.py` module containing message type definitions
- **Import_References**: All import statements that reference message types
- **Class_Definition**: The actual class definition in the constants module
- **Export_References**: The `__all__` exports in `__init__.py` files

## Requirements

### Requirement 1: Complete Import Migration

**User Story:** As a developer, I want all import statements to correctly reference DMsgType, so that the code imports the right constants without errors.

#### Acceptance Criteria

1. WHEN any module imports message types, THE import SHALL use `from .constants.DMsgType import DMsgType`
2. WHEN the import statement is processed, THE system SHALL NOT raise ImportError or AttributeError
3. THE import statements SHALL NOT reference the old `MessageType` or incorrect `DDMsgType` names
4. ALL files that import message types SHALL use the consistent import pattern
5. THE import paths SHALL be relative and correct for each module's location

### Requirement 2: Consistent Class Definition

**User Story:** As a developer, I want the message type class to be properly named DMsgType, so that the naming is consistent with the D-prefix convention.

#### Acceptance Criteria

1. THE class definition in `constants/DMsgType.py` SHALL be named `DMsgType` not `MsgType`
2. THE class SHALL maintain all existing message type values
3. THE class SHALL NOT require a backward compatibility alias
4. THE class definition SHALL follow the established D-prefix naming pattern
5. THE class SHALL be properly exported and importable as `DMsgType`

### Requirement 3: Consistent Usage Throughout Codebase

**User Story:** As a developer, I want all references to message types to use DMsgType consistently, so that the codebase has uniform naming.

#### Acceptance Criteria

1. WHEN message types are referenced in code, THE reference SHALL use `DMsgType.MESSAGE_NAME`
2. WHEN type hints are used, THE hint SHALL reference `DMsgType` not `MsgType`
3. WHEN message handlers are registered, THE message type parameter SHALL be `DMsgType`
4. ALL variable names and function parameters SHALL use `DMsgType` consistently
5. THE codebase SHALL NOT contain mixed references to old and new naming

### Requirement 4: Proper Module Exports

**User Story:** As a developer importing from the hydra_router package, I want DMsgType to be properly exported, so that I can import it from the main package.

#### Acceptance Criteria

1. THE `__init__.py` file SHALL export `DMsgType` in the `__all__` list
2. THE `__init__.py` file SHALL import `DMsgType` correctly from the constants module
3. THE export SHALL NOT reference the old `MsgType` name
4. THE package SHALL be importable as `from hydra_router import DMsgType`
5. THE exports SHALL be consistent with the actual class name

### Requirement 5: No Breaking Changes

**User Story:** As a user of the hydra_router package, I want the migration to not break existing functionality, so that my applications continue to work.

#### Acceptance Criteria

1. WHEN the migration is complete, THE existing message handling functionality SHALL work unchanged
2. WHEN messages are sent and received, THE message types SHALL be processed correctly
3. THE message type values SHALL remain the same as before the migration
4. THE API behavior SHALL be identical to the pre-migration state
5. THE migration SHALL NOT affect the runtime behavior of the system
