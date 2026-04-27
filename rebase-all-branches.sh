#!/bin/bash

# Script to rebase all PR branches onto main
# Usage: chmod +x rebase-all-branches.sh && ./rebase-all-branches.sh

set -e  # Exit on error

echo "🔄 Starting sequential rebase of all PR branches..."
echo ""

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "📍 Current branch: $CURRENT_BRANCH"
echo ""

# Ensure we're on main
echo "🚀 Checking out main branch..."
git checkout main
git pull origin main
echo "✅ main branch is up to date"
echo ""

# Array of all PR branches in order (PR #1 through #23)
BRANCHES=(
    "testing-improvement-file-parser-16326626735954480766"              # PR #1
    "code-health-remove-unused-import-shutil-10562828985536677886"      # PR #2
    "fix-flask-secret-key-vuln-16646240929171427304"                    # PR #3
    "perf-step5interaction-array-find-4254176658067026472"              # PR #4
    "test-i18n-frontend-47864235511556246"                              # PR #5
    "perf/optimize-n-plus-1-query-parallel-simulation-1271477696564710422"  # PR #6
    "perf/fix-n-plus-one-query-16246831122702315210"                    # PR #7
    "refactor-local-first-8532148507464803428"                          # PR #8
    "test-retry-functionality-86818100258579920"                        # PR #9
    "add-logger-tests-16677636688932380308"                             # PR #10
    "add-frontend-api-index-tests-11666654140120077618"                 # PR #11
    "perf/fix-follow-action-n-plus-one-17225233856938445875"           # PR #12
    "test-simulation-manager-17300382769522203724"                      # PR #13
    "refactor-prepare-simulation-12508732862508152323"                  # PR #15
    "refactor-graph-panel-d3-6959773939976821150"                       # PR #18
    "refactor-report-parser-487108557105431965"                         # PR #17
    "palette/add-aria-label-to-close-buttons-2998689821703476722"      # PR #16
    "palette/ux-accessibility-improvements-10328356023721439450"        # PR #14? or earlier
    "bolt-vue-router-code-splitting-17941176299224972655"              # PR #20
    "feature/implement-environment-setup-step-11736924636817528299"     # PR #19
    "update-readme-14837931487125420636"                                # PR #21
    "sentinel-security-hardening-10577261616740406227"                  # PR #22
    "palette-home-vue-accessibility-13442460119316587519"               # PR #23
)

SUCCESS_COUNT=0
FAILED_COUNT=0
FAILED_BRANCHES=()

# Rebase each branch
for i in "${!BRANCHES[@]}"; do
    BRANCH="${BRANCHES[$i]}"
    PR_NUM=$((i + 1))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔄 Rebasing PR #$PR_NUM: $BRANCH"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Fetch the latest from origin
    git fetch origin "$BRANCH" 2>/dev/null || {
        echo "❌ Failed to fetch $BRANCH from origin"
        FAILED_BRANCHES+=("$BRANCH")
        ((FAILED_COUNT++))
        continue
    }
    
    # Checkout the branch
    git checkout "$BRANCH" 2>/dev/null || {
        echo "❌ Failed to checkout $BRANCH"
        FAILED_BRANCHES+=("$BRANCH")
        ((FAILED_COUNT++))
        continue
    }
    
    # Rebase onto main
    if git rebase main 2>/dev/null; then
        echo "✅ Successfully rebased onto main"
        
        # Force push the rebased branch
        if git push origin "$BRANCH" --force-with-lease 2>/dev/null; then
            echo "✅ Successfully pushed $BRANCH"
            ((SUCCESS_COUNT++))
        else
            echo "⚠️  Rebase succeeded but push failed for $BRANCH"
            FAILED_BRANCHES+=("$BRANCH")
            ((FAILED_COUNT++))
        fi
    else
        echo "❌ Rebase conflict detected on $BRANCH"
        echo "   Please resolve conflicts manually:"
        echo "   - Review conflicted files: git status"
        echo "   - Resolve conflicts, then: git add ."
        echo "   - Continue rebase: git rebase --continue"
        echo "   - Force push: git push origin $BRANCH --force-with-lease"
        
        # Reset rebase
        git rebase --abort 2>/dev/null || true
        FAILED_BRANCHES+=("$BRANCH")
        ((FAILED_COUNT++))
    fi
    
    echo ""
done

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 REBASE SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Successfully rebased: $SUCCESS_COUNT branches"
echo "❌ Failed: $FAILED_COUNT branches"
echo ""

if [ $FAILED_COUNT -gt 0 ]; then
    echo "Failed branches:"
    for branch in "${FAILED_BRANCHES[@]}"; do
        echo "  - $branch"
    done
fi

echo ""
echo "🎉 Rebase operation complete!"
echo ""
echo "Next steps:"
echo "1. Check GitHub - your PRs should now be mergeable"
echo "2. If any branches still have conflicts, resolve them manually"
echo "3. Go back to main: git checkout main"
echo ""
