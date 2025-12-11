# WebRTC Implementation Validation

You are validating a WebRTC implementation in this codebase. Your goal is to ensure code quality, adherence to project standards, and proper implementation of WebRTC functionality.

## CRITICAL GIT RESTRICTIONS

❌ ABSOLUTELY FORBIDDEN (system handles these):
- `git commit` (ALL forms) - system handles ALL commits
- `git commit --amend` - NEVER (can corrupt pushed commits)
- `git push` (ALL forms) - system handles ALL pushes to correct branch

✅ ALLOWED (safe operations):
- `git status`, `git diff`, `git log`, `git show` (read-only inspection)
- `git add` (staging files is allowed)
- `git stash`, `git stash pop` (temporary storage)
- `git mv` (file operations)
- `git restore <file>`, `git checkout <file>` (reverting specific files if needed)

🚨 IF YOU FIND ERRORS:
- ✅ Fix them by EDITING specific lines with the Edit tool
- ✅ Run linting/formatting commands to auto-fix issues
- ❌ DO NOT commit or push - system handles this

## MANDATORY ISSUES TO ADDRESS

The following issues MUST be fixed:

### MAJOR Issues:
1. **No automated tests for WebRTC functionality** - Create test files for WebRTC connection, signaling, and streaming
2. **No unit tests for Python backend components** - Add tests for `main.py` and `settings.py`

### MINOR Issues:
3. **No linting configuration** - Add eslint, pylint, or flake8 configuration
4. **Hardcoded Spanish comments in JavaScript** (index.html:53) - Replace with English
5. **CORS configured with wildcard '*'** (go2rtc.yaml:21) - Document this as development-only
6. **Untracked configuration files** (.mcp.json, .prompt-file.txt) - Add to .gitignore

## VALIDATION WORKFLOW

### Phase 1: Extract Project Standards (REQUIRED)
Use MCP tools to understand the codebase:

1. **Extract Coding Standards**:
   ```
   Use extract_coding_standards tool with categories: ["naming", "formatting", "documentation", "testing"]
   Languages to check: ["python", "javascript", "typescript"]
   ```

2. **Find WebRTC Reference Implementations**:
   ```
   Use search_code_patterns with semantic=true:
   - Pattern: "webrtc" or "real-time" or "streaming"
   - Study how similar real-time features are implemented
   ```

3. **Find Test Patterns**:
   ```
   Use search_code_patterns with semantic=true:
   - Pattern: "test" or "testing" or "unittest"
   - Understand project testing conventions
   ```

4. **Locate Related Functions**:
   ```
   Use find_functions with patterns:
   - "test_*" or "*_test" (testing functions)
   - "*stream*" or "*rtc*" (WebRTC-related functions)
   ```

### Phase 2: Code Review & Validation

Review ALL WebRTC-related files:

1. **Inspect WebRTC Implementation**:
   - Read all JavaScript files handling WebRTC (likely in index.html or separate .js files)
   - Read Python backend files (main.py, settings.py)
   - Read go2rtc.yaml configuration

2. **Validate Against Standards**:
   - [ ] Naming conventions match extracted standards
   - [ ] Error handling follows project patterns found via search_code_patterns
   - [ ] Documentation style matches existing docstrings
   - [ ] Import organization matches project style
   - [ ] Code structure mirrors similar implementations

3. **WebRTC-Specific Checks**:
   - [ ] Proper error handling for connection failures
   - [ ] ICE candidate handling is robust
   - [ ] Signaling logic is clear and well-structured
   - [ ] Media stream handling includes cleanup on disconnect
   - [ ] CORS configuration documented as development-only
   - [ ] No hardcoded credentials or sensitive data

4. **Check Code Quality**:
   - [ ] No Spanish comments (fix index.html:53)
   - [ ] Consistent formatting
   - [ ] No console.log statements in production code
   - [ ] Proper async/await usage
   - [ ] Resource cleanup (close connections, remove listeners)

### Phase 3: Add Missing Tests (MANDATORY)

1. **Create WebRTC Tests**:
   - Add test file for WebRTC functionality (follow patterns from search_code_patterns)
   - Test connection establishment
   - Test signaling flow
   - Test error scenarios (connection failure, timeout)
   - Use testing framework found in project

2. **Create Python Backend Tests**:
   - Add unit tests for main.py (FFmpeg process management)
   - Add unit tests for settings.py
   - Follow testing patterns from extracted standards
   - Mock external dependencies appropriately

3. **Verify Test Coverage**:
   - Run tests to ensure they pass
   - Verify critical paths are tested

### Phase 4: Add Linting Configuration (MANDATORY)

1. **JavaScript Linting**:
   - Add .eslintrc.json or .eslintrc.js with appropriate rules
   - Run eslint and fix any issues found

2. **Python Linting**:
   - Add .pylintrc or setup.cfg with pylint/flake8 configuration
   - Run linter and fix any issues found

### Phase 5: Update .gitignore (MANDATORY)

Add these entries to .gitignore:
```
.mcp.json
.prompt-file.txt
```

## EXECUTION GUIDELINES

1. **Work systematically** - Complete each phase before moving to the next
2. **Use MCP tools first** - Always start with extract_coding_standards and search_code_patterns
3. **Document decisions** - If you deviate from found patterns, explain why
4. **Fix issues inline** - Use Edit tool to fix problems, don't just report them
5. **Run validation** - Execute tests and linters after adding them
6. **No questions** - Make reasonable decisions based on codebase analysis

## FINAL DELIVERABLE

Provide a summary report:
- ✅ Issues fixed with file locations
- ✅ Tests added with coverage details
- ✅ Linting configuration added
- ✅ Standards validated against extracted project guidelines
- ⚠️ Any remaining concerns or recommendations

Remember: Use the MCP tools (extract_coding_standards, search_code_patterns, find_functions) BEFORE making changes to ensure your fixes match the existing codebase style perfectly.

🚨 CRITICAL - DO NOT ASK QUESTIONS:
- ❌ DO NOT ASK ANY QUESTIONS
- ❌ DO NOT use AskUserQuestion tool
- ❌ DO NOT output questions as text
- ✅ Make reasonable implementation decisions based on existing patterns
- ✅ Proceed with implementation immediately
