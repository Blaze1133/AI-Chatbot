"use client"

import Link from "next/link"
import { Sparkles } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"
import { Button } from "@/components/ui/button"

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-border backdrop-blur-xl">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="text-xl font-bold text-gradient">AI Assistant</span>
        </Link>
        
        <div className="flex items-center gap-4">
          <ThemeToggle />
          <Link href="/chat">
            <Button variant="glow" size="sm">
              Try the AI
            </Button>
          </Link>
        </div>
      </div>
    </nav>
  )
}
