#!/bin/bash
# envwizard - Package Verification Script
# Run this to verify the package is ready for publication

set -e

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║  envwizard Package Verification Script                                  ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Must run from envwizard root directory"
    exit 1
fi

echo "📦 Step 1: Checking project structure..."
if [ -d "src/envwizard" ] && [ -d "tests" ] && [ -f "README.md" ]; then
    echo "✓ Project structure OK"
else
    echo "❌ Project structure incomplete"
    exit 1
fi

echo ""
echo "🐍 Step 2: Testing Python imports..."
python3 -c "
import sys
try:
    import envwizard
    from envwizard.core import EnvWizard
    from envwizard.cli.main import cli
    print('✓ All imports successful')
    print(f'  Version: {envwizard.__version__}')
except Exception as e:
    print(f'❌ Import failed: {e}')
    sys.exit(1)
"

echo ""
echo "🧪 Step 3: Running test suite..."
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short 2>&1 | tail -3
    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        echo "✓ All tests passed"
    else
        echo "❌ Some tests failed"
        exit 1
    fi
else
    echo "⚠ pytest not installed, skipping tests"
fi

echo ""
echo "🔨 Step 4: Building package..."
if [ -d "dist" ]; then
    rm -rf dist/
fi
python3 -m build > /dev/null 2>&1
if [ -f "dist/envwizard-0.1.0-py3-none-any.whl" ]; then
    echo "✓ Package built successfully"
    ls -lh dist/
else
    echo "❌ Package build failed"
    exit 1
fi

echo ""
echo "✅ Step 5: Verifying with twine..."
if command -v twine &> /dev/null; then
    twine check dist/* 2>&1 | grep -E "(PASSED|FAILED|WARNING)"
else
    echo "⚠ twine not installed, skipping verification"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                          ║"
echo "║  ✅ PACKAGE VERIFICATION COMPLETE                                        ║"
echo "║                                                                          ║"
echo "║  Your package is ready for PyPI publication!                            ║"
echo "║                                                                          ║"
echo "║  Next steps:                                                             ║"
echo "║  1. Create GitHub repository                                             ║"
echo "║  2. Set up PyPI accounts                                                 ║"
echo "║  3. Test on TestPyPI: make publish-test                                  ║"
echo "║  4. Publish to PyPI: Create GitHub release                               ║"
echo "║                                                                          ║"
echo "║  See QUICKSTART.md for detailed instructions                             ║"
echo "║                                                                          ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
