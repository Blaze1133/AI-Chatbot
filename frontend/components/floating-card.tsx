"use client"

import { motion } from "framer-motion"
import { cn } from "@/lib/utils"

interface FloatingCardProps {
  children: React.ReactNode
  className?: string
  delay?: number
  duration?: number
}

export function FloatingCard({ 
  children, 
  className, 
  delay = 0, 
  duration = 6 
}: FloatingCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ 
        opacity: 1, 
        y: 0,
      }}
      transition={{
        duration: 0.6,
        delay,
      }}
      className={cn(
        "glass rounded-2xl p-6 backdrop-blur-xl shadow-lg dark:shadow-none",
        className
      )}
      style={{
        animation: `float ${duration}s ease-in-out infinite`,
        animationDelay: `${delay}s`,
      }}
    >
      {children}
    </motion.div>
  )
}
