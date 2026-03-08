# AI SaaS Website - Premium Frontend

A modern, futuristic AI SaaS landing page and chat interface built with Next.js, React, TailwindCSS, Framer Motion, and Shadcn UI.

## Features

- 🎨 **Modern Design**: Dark elegant theme with futuristic gradients and glassmorphism
- ✨ **Smooth Animations**: Powered by Framer Motion for fluid interactions
- 📱 **Responsive**: Beautiful on desktop, tablet, and mobile
- 🚀 **Performance**: Built with Next.js 14 App Router
- 🎯 **Premium UI**: Inspired by Vercel, Linear, and modern AI products

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **UI Components**: Shadcn UI

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the website.

### Build

```bash
npm run build
npm start
```

## Project Structure

```
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   ├── chat/
│   │   └── page.tsx        # Chat interface
│   └── globals.css         # Global styles
├── components/
│   ├── ui/                 # UI components (Button, Card)
│   ├── animated-gradient.tsx
│   ├── feature-card.tsx
│   ├── floating-card.tsx
│   └── particles.tsx
├── sections/
│   ├── hero.tsx            # Hero section
│   ├── features.tsx        # Features showcase
│   ├── product-demo.tsx    # Product demo
│   ├── how-it-works.tsx    # How it works
│   └── cta.tsx             # Call to action
└── lib/
    └── utils.ts            # Utility functions
```

## Sections

1. **Hero**: Full-screen landing with animated gradients and floating cards
2. **Features**: Grid of feature cards with hover animations
3. **Product Demo**: Interactive chat UI mockup
4. **How It Works**: Step-by-step process visualization
5. **CTA**: Call-to-action section
6. **Chat Page**: Dedicated AI chat interface

## Customization

### Colors

Edit the color scheme in `app/globals.css`:

```css
:root {
  --background: 222 47% 4%;
  --foreground: 210 40% 98%;
  --primary: 217 91% 60%;
  /* ... */
}
```

### Animations

Customize animations in `tailwind.config.ts`:

```typescript
animation: {
  'float': 'float 6s ease-in-out infinite',
  // Add more animations
}
```

## License

MIT
