"use client"

import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { FloatingCard } from "@/components/floating-card"
import { AnimatedGradient } from "@/components/animated-gradient"
import { Particles } from "@/components/particles"
import { Sparkles, Zap, Brain } from "lucide-react"
import Link from "next/link"

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16 md:pt-20">
      <AnimatedGradient />
      <Particles />
      
      <div className="container relative z-10 px-4 py-20 md:py-32">
        <div className="max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-block mb-6"
            >
              <div className="glass rounded-full px-6 py-2 text-sm font-medium">
                <span className="text-gradient">Powered by Advanced AI</span>
              </div>
            </motion.div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl xl:text-8xl font-bold mb-4 md:mb-6 leading-tight px-2">
              <span className="text-gradient glow-text">
                Your AI Knowledge
              </span>
              <br />
              <span className="text-foreground">Assistant</span>
            </h1>

            <p className="text-lg md:text-xl lg:text-2xl text-muted-foreground mb-8 md:mb-12 max-w-3xl mx-auto px-4">
              Get instant, intelligent answers from your documentation. 
              Powered by cutting-edge AI that understands context and delivers precision.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link href="/chat">
                <Button variant="glow" size="lg" className="group">
                  Try the AI
                  <Sparkles className="ml-2 h-5 w-5 group-hover:rotate-12 transition-transform" />
                </Button>
              </Link>
              <Button variant="outline" size="lg">
                Learn more
              </Button>
            </div>
          </motion.div>

          <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <FloatingCard delay={0.2} duration={6}>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Zap className="h-5 w-5 text-blue-400" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold">Ask Anything</h3>
                  <p className="text-sm text-muted-foreground">Natural language queries</p>
                </div>
              </div>
            </FloatingCard>

            <FloatingCard delay={0.4} duration={7}>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Brain className="h-5 w-5 text-purple-400" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold">Instant Answers</h3>
                  <p className="text-sm text-muted-foreground">Lightning-fast responses</p>
                </div>
              </div>
            </FloatingCard>

            <FloatingCard delay={0.6} duration={8}>
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-pink-500/20 flex items-center justify-center">
                  <Sparkles className="h-5 w-5 text-pink-400" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold">Powered by AI</h3>
                  <p className="text-sm text-muted-foreground">Advanced intelligence</p>
                </div>
              </div>
            </FloatingCard>
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  )
}
