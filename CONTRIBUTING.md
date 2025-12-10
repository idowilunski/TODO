# Contributing to TODO App - Professional Git Workflow

## 🎯 Overview
This guide teaches you how to work like a professional developer using Git for version control, feature branches, and collaboration.

---

## 📋 Table of Contents
1. [Git Workflow Fundamentals](#git-workflow-fundamentals)
2. [Branch Strategy](#branch-strategy)
3. [Commit Conventions](#commit-conventions)
4. [Feature Development Process](#feature-development-process)
5. [Pull Request Best Practices](#pull-request-best-practices)
6. [Common Commands](#common-commands)
7. [Troubleshooting](#troubleshooting)

---

## 🔄 Git Workflow Fundamentals

### The Golden Rule
> **Never commit directly to `main`**  
> Always develop features in separate branches and merge via Pull Requests (PRs).

### Why?
- **Safety**: main branch stays stable for production
- **Review**: Code gets reviewed before merging
- **History**: Clean, traceable change history
- **Collaboration**: Multiple people can work simultaneously
- **Rollback**: Easy to revert bad changes

---

## 🌳 Branch Strategy

### Branch Types

#### 1. **`main` (or `master`)** - Production Branch
- **Purpose**: Stable, deployable code
- **Rules**: 
  - ✅ Only merge via approved PRs
  - ❌ Never commit directly
  - ✅ Should always build and pass tests

#### 2. **Feature Branches** - Development Work
- **Naming**: `feature/short-description`
  ```bash
  feature/async-research
  feature/bulk-delete
  feature/serpapi-integration
  ```

#### 3. **Bug Fix Branches** - Fix Production Issues
- **Naming**: `fix/bug-description`
  ```bash
  fix/research-status-error
  fix/delete-all-confirmation
  ```

#### 4. **Hotfix Branches** - Urgent Production Fixes
- **Naming**: `hotfix/critical-issue`
  ```bash
  hotfix/security-vulnerability
  hotfix/database-crash
  ```

#### 5. **Experimental Branches** - Try New Ideas
- **Naming**: `experiment/idea` or just `try`, `test`
  ```bash
  experiment/ollama-integration
  try  # Your current branch!
  ```

### Branch Lifecycle
```
main
  └── feature/new-feature  ← Create branch
        ├── commit 1       ← Develop
        ├── commit 2       ← Test
        └── commit 3       ← Done
              └── PR → main  ← Merge back
```

---

## 📝 Commit Conventions

### Conventional Commits Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Formatting, missing semicolons (no code change)
- **refactor**: Code restructuring (no feature change)
- **perf**: Performance improvement
- **test**: Adding tests
- **chore**: Build process, dependencies, configs

### Examples

#### ✅ Good Commits
```bash
feat(agent): Add async research with OpenAI function calling

- Implement AgentProvider abstraction
- Add background threading for non-blocking UI
- Support OpenAI and Ollama providers
- Include graceful SerpAPI fallback

Closes #23
```

```bash
fix(tasks): Prevent bulk delete without confirmation

Users accidentally deleted all tasks. Added window.confirm()
dialog before executing DELETE /api/tasks/bulk-delete.

Fixes #45
```

```bash
docs(README): Add setup instructions for Python 3.14

Added venv creation, dependency installation, and common
troubleshooting for Windows users.
```

#### ❌ Bad Commits
```bash
fixed stuff
```
```bash
WIP
```
```bash
asdfasdf
```
```bash
Updated files
```

### Commit Size
- **Atomic**: One logical change per commit
- **Small**: Easier to review and revert
- **Complete**: Should not break the build

```bash
# ❌ Too big - multiple features
feat: Add research, bulk delete, and SerpAPI integration

# ✅ Split into 3 commits
feat(agent): Add async agent research with threading
feat(tasks): Add bulk delete endpoint
feat(agent): Integrate SerpAPI with fallback
```

---

## 🚀 Feature Development Process

### Step-by-Step Workflow

#### 1. **Start from Clean `main`**
```bash
# Switch to main
git checkout main

# Get latest changes from GitHub
git pull origin main
```

#### 2. **Create Feature Branch**
```bash
# Create and switch to new branch
git checkout -b feature/my-new-feature

# Verify you're on the new branch
git branch  # * should be next to your feature
```

#### 3. **Develop & Commit Frequently**
```bash
# Make changes to files...

# Check what changed
git status
git diff

# Stage specific files
git add apps/server/app/routes/tasks.py
git add apps/front/src/App.tsx

# Or stage everything
git add -A

# Commit with descriptive message
git commit -m "feat(tasks): Add research endpoint"

# Continue developing...
# Commit after each logical change (every 30-60 mins)
```

#### 4. **Push to GitHub Regularly**
```bash
# First push (creates remote branch)
git push -u origin feature/my-new-feature

# Subsequent pushes
git push
```

#### 5. **Keep Branch Updated with `main`**
```bash
# If main has new commits while you work:
git checkout main
git pull origin main
git checkout feature/my-new-feature
git merge main  # Or: git rebase main (advanced)

# Resolve conflicts if any, then:
git push
```

#### 6. **Create Pull Request (PR)**
- Go to GitHub repository
- Click "Compare & pull request"
- Fill in description:
  ```markdown
  ## What
  Added async agent research feature
  
  ## Why
  Users needed non-blocking UI when researching tasks
  
  ## How
  - Threading with background workers
  - Polling status every 2 seconds
  - AgentProvider abstraction for OpenAI/Ollama
  
  ## Testing
  - [x] Research completes successfully
  - [x] UI stays responsive during research
  - [x] Error handling works
  
  Closes #23
  ```

#### 7. **Code Review & Merge**
- Wait for review (or self-review for personal projects)
- Address feedback with new commits
- Once approved: **Squash and merge** or **Merge**
- Delete feature branch after merge

#### 8. **Clean Up Local Branch**
```bash
# Switch back to main
git checkout main

# Pull merged changes
git pull origin main

# Delete local feature branch
git branch -d feature/my-new-feature
```

---

## 🔍 Pull Request Best Practices

### PR Title
```
feat(agent): Add async research with OpenAI function calling
```
Use same convention as commits.

### PR Description Template
```markdown
## 🎯 What
Brief summary of changes

## 💡 Why
Problem being solved or feature need

## 🔧 How
Technical approach and key decisions

## 📸 Screenshots
(if UI changes)

## ✅ Testing Done
- [ ] Manual testing
- [ ] Unit tests added
- [ ] Integration tests pass
- [ ] No console errors

## 📝 Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No commented-out code
- [ ] Environment variables documented in .env.example
- [ ] Breaking changes noted

## 🔗 Related Issues
Closes #23
Refs #45
```

### PR Size
- **Small**: 50-300 lines changed (ideal)
- **Medium**: 300-500 lines (acceptable)
- **Large**: 500+ lines (split into multiple PRs)

### Review Process
1. **Self-review first**: Check your own diff on GitHub
2. **Request review**: Tag teammates
3. **Respond to feedback**: Be open to suggestions
4. **Update PR**: Push new commits addressing feedback
5. **Merge**: Once approved

---

## 🛠️ Common Commands

### Daily Workflow
```bash
# See current branch and status
git status
git branch

# See what changed
git diff                    # Unstaged changes
git diff --staged           # Staged changes
git diff main..HEAD         # All commits on current branch

# Commit workflow
git add file.py             # Stage specific file
git add -A                  # Stage all changes
git commit -m "message"     # Commit
git push                    # Push to GitHub

# Switch branches
git checkout main           # Switch to main
git checkout -b feature/x   # Create and switch to new branch

# Update from remote
git pull                    # Fetch + merge current branch
git pull origin main        # Pull specific branch

# View history
git log --oneline           # Compact log
git log --graph --oneline   # Visual branch graph
```

### Undo Commands (Use Carefully!)
```bash
# Unstage files (keep changes)
git restore --staged file.py

# Discard changes to file (DESTRUCTIVE)
git restore file.py
git checkout -- file.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes - DESTRUCTIVE)
git reset --hard HEAD~1

# Amend last commit message
git commit --amend -m "New message"

# Amend last commit with new changes
git add forgotten-file.py
git commit --amend --no-edit
```

### Branch Management
```bash
# List all branches
git branch              # Local only
git branch -a           # Including remote

# Delete branch
git branch -d feature/x         # Safe delete (merged only)
git branch -D feature/x         # Force delete

# Rename branch
git branch -m old-name new-name

# Push deletion to remote
git push origin --delete feature/x
```

### Stash (Temporary Save)
```bash
# Save uncommitted changes
git stash
git stash save "WIP: half-done feature"

# List stashes
git stash list

# Apply stash
git stash pop           # Apply and remove
git stash apply         # Apply but keep stash

# Drop stash
git stash drop stash@{0}
```

---

## 🆘 Troubleshooting

### "I committed to `main` by mistake!"
```bash
# Create branch from current state
git branch feature/my-work

# Reset main to match remote
git reset --hard origin/main

# Switch to feature branch
git checkout feature/my-work

# Now push feature branch
git push -u origin feature/my-work
```

### "I have merge conflicts!"
```bash
# After git merge main
# Files with conflicts marked as "both modified"

# Open conflicted files, look for:
<<<<<<< HEAD
your changes
=======
main branch changes
>>>>>>> main

# Edit file to keep what you want, remove markers
# Then:
git add file.py
git commit -m "Merge main into feature/x"
```

### "I want to undo my last push!"
```bash
# CAUTION: Only if you're the only one using the branch!
git reset --hard HEAD~1   # Remove last commit locally
git push --force          # Overwrite remote

# Safer: Revert (creates new commit undoing old one)
git revert HEAD
git push
```

### "My branch is way behind `main`"
```bash
git checkout main
git pull origin main
git checkout feature/my-branch

# Option 1: Merge (preserves all history)
git merge main

# Option 2: Rebase (cleaner history, advanced)
git rebase main
# If conflicts: fix, then git rebase --continue
```

### "I need to switch branches but have uncommitted changes"
```bash
# Option 1: Commit them
git add -A
git commit -m "WIP: Save progress"

# Option 2: Stash them
git stash
git checkout other-branch
# Later:
git checkout original-branch
git stash pop
```

---

## 🏆 Pro Tips

### 1. **Commit Often, Push Daily**
- Commit every 30-60 minutes (atomic changes)
- Push to GitHub at least once per day
- Protects against data loss

### 2. **Write Descriptive Messages**
```bash
# ❌ Bad
git commit -m "fix"

# ✅ Good
git commit -m "fix(tasks): Handle null research_status in to_dict()"
```

### 3. **Use `.gitignore`**
Never commit:
- Environment files (`.env`)
- Dependencies (`node_modules/`, `.venv/`)
- Build output (`dist/`, `build/`)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Databases (`*.db`, `*.sqlite`)

### 4. **Review Your Own Diffs**
```bash
# Before committing
git diff

# Before pushing
git diff origin/main..HEAD
```

### 5. **Use Aliases (Optional)**
```bash
# Add to ~/.gitconfig
[alias]
    st = status
    co = checkout
    br = branch
    cm = commit -m
    lg = log --graph --oneline --all

# Usage
git st    # same as git status
git co main
git cm "feat: new feature"
```

### 6. **Keep Branches Short-Lived**
- Feature branches: 1-3 days ideal, max 1 week
- Merge frequently to avoid conflicts
- Delete after merging

### 7. **Test Before Committing**
```bash
# Run tests
npm test
python -m pytest

# Start app and verify
npm start
python run.py

# Then commit
git add -A
git commit -m "feat: working feature with tests"
```

---

## 📚 Additional Resources

### Learning Git
- [Git Book (Official)](https://git-scm.com/book/en/v2)
- [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials)
- [Oh Shit, Git!?!](https://ohshitgit.com/) - Fix common mistakes

### GitHub
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Pull Request Best Practices](https://github.blog/2015-01-21-how-to-write-the-perfect-pull-request/)

### Conventional Commits
- [Conventional Commits Spec](https://www.conventionalcommits.org/)

---

## 🎓 Your Next Steps

1. **Practice**: Create feature branches for every new feature
2. **Commit frequently**: Aim for 3-5 commits per feature
3. **Write good messages**: Use conventional commit format
4. **Review your work**: Check diffs before pushing
5. **Clean up**: Delete merged branches
6. **Learn gradually**: Start with basics, add advanced techniques over time

**Remember**: Even professional developers make Git mistakes. The key is learning how to fix them!
