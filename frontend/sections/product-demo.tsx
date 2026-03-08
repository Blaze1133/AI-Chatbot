"use client"

import React, { useState, useEffect } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Upload, FileSearch, MessageSquare, CheckCircle2 } from "lucide-react"

export function ProductDemo() {
  const [currentSlide, setCurrentSlide] = useState(0)

  const slides = [
    {
      question: "What are the main conclusions of this research paper?",
      answer: "The research demonstrates that the proposed neural architecture achieves 94% accuracy on classification tasks, outperforming baseline methods by 23%. The study concludes that this approach is highly effective for real-world applications.",
      source: "research_paper.pdf - Page 12",
    },
    {
      question: "Can you summarize the methodology used in chapter 3?",
      answer: "Chapter 3 describes a mixed-methods approach combining quantitative surveys (n=500) with qualitative interviews (n=25). The study used stratified random sampling and thematic analysis for data interpretation.",
      source: "thesis_document.pdf - Page 45",
    },
    {
      question: "What safety precautions are mentioned for this equipment?",
      answer: "The manual specifies three critical safety measures: 1) Always wear protective gear, 2) Ensure proper ventilation, and 3) Never operate without emergency shutdown access. Regular maintenance checks are required every 30 days.",
      source: "equipment_manual.pdf - Page 8",
    },
  ]

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % slides.length)
    }, 4000)
    return () => clearInterval(timer)
  }, [])

  return (
    <section className="relative py-16 md:py-32 px-4 overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-amber-500/5 dark:via-blue-500/5 to-transparent" />
      
      <div className="container mx-auto relative z-10">
        <div className="text-center mb-12 md:mb-16 px-4">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mb-4">
            <span className="text-gradient">See It In Action</span>
          </h2>
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
            Watch how our AI transforms your documents into interactive conversations
          </p>
        </div>

        <div className="max-w-5xl mx-auto">
          <div className="relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={currentSlide}
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.5 }}
                className="glass rounded-3xl p-6 md:p-10 glow-border"
              >
                <div className="space-y-6">
                  {/* User Question */}
                  <div className="flex gap-3 items-start">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-amber-500 to-orange-500 dark:from-blue-500 dark:to-purple-600 flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 bg-gradient-to-br from-amber-500 to-orange-500 dark:from-blue-600 dark:to-blue-500 text-white rounded-2xl rounded-tl-none p-4 shadow-lg">
                      <p className="text-sm md:text-base leading-relaxed">
                        {slides[currentSlide].question}
                      </p>
                    </div>
                  </div>

                  {/* AI Answer */}
                  <div className="flex gap-3 items-start flex-row-reverse">
                    <div className="h-10 w-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 dark:from-purple-500 dark:to-pink-600 flex items-center justify-center flex-shrink-0">
                      <CheckCircle2 className="h-5 w-5 text-white" />
                    </div>
                    <div className="flex-1 bg-card border border-border rounded-2xl rounded-tr-none p-4 shadow-lg">
                      <p className="text-sm md:text-base text-foreground leading-relaxed mb-3">
                        {slides[currentSlide].answer}
                      </p>
                      <div className="border-t border-border/50 pt-3">
                        <p className="text-xs font-semibold text-amber-600 dark:text-blue-400 mb-1">📄 Source:</p>
                        <div className="bg-amber-50 dark:bg-black/30 rounded-lg p-2">
                          <p className="text-xs text-amber-700 dark:text-blue-300 font-medium">
                            {slides[currentSlide].source}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Slide Indicators */}
            <div className="flex justify-center gap-3 mt-8">
              {slides.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentSlide(index)}
                  className={`h-2 rounded-full transition-all duration-300 ${
                    index === currentSlide
                      ? "w-12 bg-gradient-to-r from-amber-500 to-orange-500 dark:from-blue-500 dark:to-purple-600"
                      : "w-2 bg-muted-foreground/30 hover:bg-muted-foreground/50"
                  }`}
                  aria-label={`Go to slide ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
