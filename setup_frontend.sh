#!/bin/bash
# Frontend setup script for Phase 6

echo "=================================="
echo "Phase 6: Frontend Foundation Setup"
echo "=================================="

cd frontend

# Check if Next.js is already initialized
if [ -f "package.json" ]; then
    echo "Frontend already initialized. Skipping create-next-app."
else
    echo "Creating Next.js 14 application..."
    npx create-next-app@latest . --typescript --tailwind --app --no-src-dir --import-alias "@/*"
fi

echo ""
echo "Installing additional dependencies..."
npm install @tanstack/react-query axios recharts d3 lucide-react

echo ""
echo "Installing shadcn/ui..."
npx shadcn@latest init -y -d

echo ""
echo "Adding shadcn/ui components..."
npx shadcn@latest add button card input dialog progress badge

echo ""
echo "=================================="
echo "Frontend setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  cd frontend"
echo "  npm run dev"
