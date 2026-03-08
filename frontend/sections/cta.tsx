"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Sparkles } from "lucide-react"
import Link from "next/link"

export function CTA() {
  return (
    <section className="relative py-16 md:py-32 px-4">
      <div className="container mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="max-w-4xl mx-auto text-center px-2"
        >
          <div className="relative group">
            {/* Animated Gradient Border */}
            <div className="absolute -inset-1 bg-gradient-to-r from-amber-500 via-orange-500 to-yellow-500 dark:from-blue-600 dark:via-purple-600 dark:to-pink-600 rounded-3xl opacity-75 group-hover:opacity-100 blur-sm animate-gradient-rotate" />
            
            <div className="relative glass rounded-3xl p-6 sm:p-8 md:p-12 lg:p-16 bg-background">
              <h2 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-6">
                <span className="text-gradient">
                  Ready to Chat with
                  <br />
                  Your Documents?
                </span>
              </h2>
              <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
                Upload any PDF and start getting instant answers. No setup required.
              </p>
              <Link href="/chat">
                <Button variant="glow" size="lg" className="group text-lg px-12 py-6 h-auto">
                  Try the AI Now
                  <Sparkles className="ml-2 h-6 w-6 group-hover:rotate-12 transition-transform" />
                </Button>
              </Link>
              <p className="text-sm text-muted-foreground mt-6">
                No credit card required • Free to start
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
