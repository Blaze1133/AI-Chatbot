import { Navbar } from "@/components/navbar"
import { Hero } from "@/sections/hero"
import { Features } from "@/sections/features"
import { ProductDemo } from "@/sections/product-demo"
import { HowItWorks } from "@/sections/how-it-works"
import { CTA } from "@/sections/cta"

export default function Home() {
  return (
    <main className="relative">
      <Navbar />
      <Hero />
      <Features />
      <ProductDemo />
      <HowItWorks />
      <CTA />
      <footer className="border-t border-border/40 py-6 bg-background/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 text-center">
          <p className="text-sm text-muted-foreground">
            © {new Date().getFullYear()} Mainkanjkata Tej. All rights reserved.
          </p>
        </div>
      </footer>
    </main>
  )
}
