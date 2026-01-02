# Implementation Plan: DMsgType Migration

## Overview

This implementation plan systematically completes the migration from MessageType to DMsgType constants. The approach involves updating the class definition, fixing import statements, correcting exports, and validating the changes through comprehensive testing.

## Tasks

- [x] 1. Update DMsgType class definition
  - Change class name from `MsgType` to `DMsgType` in `constants/DMsgType.py`
  - Remove the backward compatibility alias `DMsgType = MsgType`
  - Ensure all enum values are preserved exactly
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 1.1 Write unit test for class definition
  - Test that class is named `DMsgType`
  - Test that no `MsgType` alias exists
  - Test that all enum values are preserved
  - _Requirements: 2.1, 2.3, 2.5_

- [x] 2. Fix import statements in all modules
  - Update `mq_client.py`: change `from .constants.DDMsgType import DDMsgType` to `from .constants.DMsgType import DMsgType`
  - Update `simple_client.py`: change `from .constants.DDMsgType import DMsgType` to `from .constants.DMsgType import DMsgType`
  - Update `simple_server.py`: change `from .constants.DDMsgType import DMsgType` to `from .constants.DMsgType import DMsgType`
  - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [ ]* 2.1 Write property test for import correctness
  - **Property 1: Import Statement Correctness**
  - **Validates: Requirements 1.2, 1.4, 1.5**

- [x] 3. Update package exports in __init__.py
  - Change `__all__` list from `"MsgType"` to `"DMsgType"`
  - Verify import statement is correct: `from .constants.DMsgType import DMsgType`
  - _Requirements: 4.1, 4.2, 4.3, 4.5_

- [ ]* 3.1 Write unit tests for package exports
  - Test that `DMsgType` is in `__all__` list
  - Test that `MsgType` is not in `__all__` list
  - Test that `from hydra_router import DMsgType` works
  - _Requirements: 4.1, 4.3, 4.4_

- [x] 4. Validate consistent usage throughout codebase
  - Scan all files to ensure consistent `DMsgType` usage in type hints
  - Verify message handler registrations use `DMsgType`
  - Check that no old naming patterns remain
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ]* 4.1 Write property test for consistent usage
  - **Property 2: Consistent DMsgType Usage**
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 5. Checkpoint - Verify imports and basic functionality
  - Ensure all modules can be imported without errors
  - Test that DMsgType can be imported from main package
  - Verify no ImportError or AttributeError exceptions
  - _Requirements: 1.2, 4.4_

- [ ]* 5.1 Write property test for enum value preservation
  - **Property 3: Enum Value Preservation**
  - **Validates: Requirements 2.2, 5.3**

- [x] 6. Run existing tests to ensure no regressions
  - Execute full test suite to verify functionality is preserved
  - Check that message handling operations work correctly
  - Confirm no breaking changes in API behavior
  - _Requirements: 5.1, 5.2, 5.4, 5.5_

- [ ]* 6.1 Write property test for functional preservation
  - **Property 4: Functional Preservation**
  - **Validates: Requirements 5.1, 5.2, 5.4, 5.5**

- [x] 7. Final validation and cleanup
  - Perform final scan for any remaining old references
  - Verify all requirements are met
  - Ensure migration is complete and consistent
  - _Requirements: 3.5, 4.5_

- [x] 8. Final checkpoint - Complete migration validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The migration preserves all enum values to maintain backward compatibility
- Each step builds on the previous to ensure systematic completion
- Property tests validate universal correctness across the codebase
- Unit tests validate specific examples and edge cases
- The migration is low-risk as it only involves naming consistency changes
