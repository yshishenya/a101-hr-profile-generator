# E2E Tests for HR Profile Generator

End-to-end tests using Playwright for comprehensive workflow testing.

## Prerequisites

- Backend API running on `http://localhost:8001`
- Frontend dev server on `http://localhost:5173` (automatically started by Playwright)
- Chromium browser installed (via `npx playwright install chromium`)

## Test Structure

```
e2e/
├── README.md                    # This file
└── profile-versioning.spec.ts   # Profile versions management tests
```

## Running Tests

### All tests (headless)
```bash
npm run test:e2e
```

### Interactive UI mode
```bash
npm run test:e2e:ui
```

### Headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Debug mode (step through tests)
```bash
npm run test:e2e:debug
```

### View test report
```bash
npm run test:e2e:report
```

## Test Coverage

### Profile Versioning Workflow (`profile-versioning.spec.ts`)

#### 1. Versions List Display (5 tests)
- Display versions timeline
- Display version metadata (username, timestamp)
- Display current version badge
- Display version type badges (generated/edited)
- Display quality scores

#### 2. Set Active Version (2 tests)
- Set old version as active
- Verify current version cannot be set as active

#### 3. Download Version (4 tests)
- Download in JSON format
- Download in Markdown format
- Download in DOCX format
- Verify download menu for all versions

#### 4. Delete Version (3 tests)
- Delete non-current version successfully
- Verify current version cannot be deleted
- Verify last version cannot be deleted

#### 5. Navigation and State (3 tests)
- Persist state when switching tabs
- Close and reopen modal correctly
- Display version count badge

#### 6. Error Handling (3 tests)
- Display loading state
- Handle network errors gracefully
- Allow retry after error

#### 7. Accessibility (2 tests)
- Proper ARIA roles and labels
- Keyboard navigation support

**Total: 22+ test scenarios**

## Test Data Requirements

Tests assume the following data exists in the backend:

- At least one profile with position name matching "Главный бухгалтер"
- Profile should have at least 2 versions for full test coverage
- Versions should have metadata (created_at, created_by_username)
- Quality scores are optional but recommended for full coverage

## Configuration

Test configuration is in `/frontend-vue/playwright.config.ts`:

- **Timeout**: 60s per test
- **Retries**: 2 on CI, 0 locally
- **Workers**: 1 on CI, parallel locally
- **Base URL**: http://localhost:5173
- **Screenshots**: On failure only
- **Videos**: Retained on failure
- **Trace**: On first retry

## CI/CD Integration

Add to your CI pipeline:

```yaml
# GitHub Actions example
- name: Install Playwright
  run: npx playwright install chromium

- name: Run E2E tests
  run: npm run test:e2e
  env:
    CI: true

- name: Upload test report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Debugging Failed Tests

1. **View HTML report**:
   ```bash
   npm run test:e2e:report
   ```

2. **Run in headed mode**:
   ```bash
   npm run test:e2e:headed
   ```

3. **Debug specific test**:
   ```bash
   npx playwright test --debug -g "should set old version as active"
   ```

4. **Check screenshots**:
   Failed tests save screenshots to `test-results/`

5. **View traces**:
   Open trace viewer for detailed timeline:
   ```bash
   npx playwright show-trace test-results/.../trace.zip
   ```

## Best Practices

### Writing New Tests

1. **Use helper functions** for common actions:
   ```typescript
   await navigateToProfiles(page)
   await openProfile(page, 'Position Name')
   await switchToVersionsTab(page)
   ```

2. **Wait for elements properly**:
   ```typescript
   await expect(element).toBeVisible({ timeout: 5000 })
   ```

3. **Use semantic selectors**:
   ```typescript
   page.getByRole('button', { name: /действия/i })  // Good
   page.locator('.v-btn')                            // Avoid
   ```

4. **Handle dynamic content**:
   ```typescript
   await page.waitForLoadState('networkidle')
   ```

5. **Test error states**:
   ```typescript
   await page.context().setOffline(true)
   // Verify error handling
   await page.context().setOffline(false)
   ```

### Test Organization

- Group related tests with `test.describe()`
- Use descriptive test names: "should [expected behavior]"
- Skip tests conditionally when data requirements not met
- Clean up after tests if they modify data

## Troubleshooting

### Tests timeout

- Increase timeout in `playwright.config.ts`
- Check backend is running and responsive
- Verify network connectivity

### Cannot find elements

- Use Playwright Inspector: `npm run test:e2e:debug`
- Check if elements are inside shadow DOM
- Verify element selectors are correct

### Flaky tests

- Add proper waits (`waitForLoadState`, `waitForTimeout`)
- Avoid race conditions with explicit expects
- Use `retry` option for unstable network calls

### Backend not ready

- Ensure backend starts before tests
- Add health check in `beforeAll` hook
- Use longer `webServer.timeout` in config

## Performance

- Tests run in parallel by default (workers: undefined)
- Each test is independent and can run in any order
- Full test suite should complete in < 5 minutes

## Future Enhancements

- [ ] Add visual regression tests
- [ ] Test multiple user roles
- [ ] Test profile editing workflow (Week 7)
- [ ] Add performance monitoring
- [ ] Test mobile viewport
- [ ] Add cross-browser testing (Firefox, Safari)

## Related Documentation

- [Frontend Architecture](../.memory_bank/architecture/frontend_architecture.md)
- [Frontend Coding Standards](../.memory_bank/guides/frontend_coding_standards.md)
- [Testing Strategy](../.memory_bank/guides/testing_strategy.md)
- [Playwright Documentation](https://playwright.dev/docs/intro)
