"use client"

import { FeatureCard } from "@/components/feature-card"
import { Search, Zap, Database, Code, Sparkles, Shield } from "lucide-react"

export function Features() {
  const features = [
    {
      icon: Search,
      title: "AI Documentation Search",
      description: "Search through your entire knowledge base with natural language. Our AI understands context and intent.",
    },
    {
      icon: Zap,
      title: "Instant Answers",
      description: "Get precise answers in milliseconds. No more scrolling through endless documentation pages.",
    },
    {
      icon: Database,
      title: "Multi-source Knowledge",
      description: "Connect multiple data sources and let AI synthesize information from all of them seamlessly.",
    },
    {
      icon: Code,
      title: "Developer Friendly",
      description: "Built for developers with code examples, API references, and technical documentation support.",
    },
    {
      icon: Sparkles,
      title: "Smart Retrieval",
      description: "Advanced semantic search that understands what you're looking for, not just keywords.",
    },
    {
      icon: Shield,
      title: "Secure & Private",
      description: "Enterprise-grade security with data encryption and privacy controls built-in.",
    },
  ]

  return (
    <section className="relative py-32 px-4">
      <div className="container mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-gradient">Powerful Features</span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to transform how you interact with documentation
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
          {features.map((feature, index) => (
            <FeatureCard
              key={feature.title}
              icon={feature.icon}
              title={feature.title}
              description={feature.description}
              delay={index * 0.1}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
