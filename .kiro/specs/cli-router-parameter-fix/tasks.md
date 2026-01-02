# Implementation Plan: CLI Router Parameter Fix

## Overview

This implementation plan addresses the parameter mismatch between the CLI and HydraRouter constructor. The fix involves updating a single line of code to use the correct parameter names, along with appropriate testing to ensure the fix works correctly.

## Tasks

- [x] 1. Fix CLI parameter mapping
  - Update the HydraRouter constructor call in cli.py to use correct parameter names
  - Change `address=args.address, port=args.port` to `router_address=args.address, router_port=args.port`
  - _Requirements: 1.1, 1.2, 1.3, 1.4_

- [ ]* 2. Write unit test for parameter mapping
  - Create test to verify CLI arguments map correctly to HydraRouter parameters
  - Test that HydraRouter can be instantiated with CLI arguments without TypeError
  - _Requirements: 2.2, 2.3_

- [ ]* 3. Write integration test for CLI startup
  - Test complete CLI workflow from argument parsing to router creation
  - Verify router starts successfully with specified address and port
  - _Requirements: 1.3, 1.5_

- [ ] 4. Verify existing tests still pass
  - Run existing test suite to ensure no regressions
  - Confirm all router functionality works after the parameter fix
  - _Requirements: 1.5, 3.1_

- [ ] 5. Test CLI functionality manually
  - Test `hydra-router start --address 127.0.0.1 --port 5556` command
  - Verify router starts without TypeError
  - Confirm router binds to correct address and port
  - _Requirements: 1.1, 1.3, 3.2_

- [ ] 6. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The core fix is a single line change in cli.py
- Testing ensures the fix works correctly and doesn't introduce regressions
- This is a low-risk change that addresses a critical bug preventing CLI usage
