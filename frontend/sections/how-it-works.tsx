"use client"

import { motion } from "framer-motion"
import { Upload, FileText, MessageSquare, Sparkles, ArrowRight } from "lucide-react"

export function HowItWorks() {
  const steps = [
    {
      icon: Upload,
      title: "Upload Your Document",
      description: "Upload any PDF document - research papers, manuals, reports, or books.",
    },
    {
      icon: FileText,
      title: "AI Processes Content",
      description: "Our AI reads and understands your document, breaking it into semantic chunks.",
    },
    {
      icon: MessageSquare,
      title: "Ask Questions",
      description: "Chat naturally with your document. Ask anything about its content.",
    },
    {
      icon: Sparkles,
      title: "Get Smart Answers",
      description: "Receive accurate answers with exact page references and source citations.",
    },
  ]

  return (
    <section className="relative py-32 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-12 md:mb-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-6 px-4">
              <span className="text-gradient">
                How It Works
              </span>
            </h2>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Transform any PDF into an interactive knowledge base in seconds
            </p>
          </motion.div>
        </div>

        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 md:gap-8 relative">
            {steps.map((step, index) => (
              <motion.div
                key={step.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="relative"
              >
                <div className="relative group">
                  <div className="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300 opacity-0 group-hover:opacity-100" />
                  <div className="relative bg-card/80 backdrop-blur-sm rounded-2xl p-8 h-full border border-border/50 hover:border-blue-500/50 transition-all duration-300">
                    <div className="mb-6">
                      <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-br from-amber-500 to-orange-500 dark:from-blue-500 dark:to-purple-600 rounded-2xl blur-md opacity-50" />
                        <div className="relative h-16 w-16 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-500 dark:from-blue-500 dark:to-purple-600 flex items-center justify-center mb-4 shadow-lg">
                          <step.icon className="h-8 w-8 text-white" />
                        </div>
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold mb-3 text-foreground">{step.title}</h3>
                    <p className="text-muted-foreground leading-relaxed">{step.description}</p>
                  </div>
                </div>

                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-6 z-20">
                    <ArrowRight className="h-6 w-6 text-purple-500" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
