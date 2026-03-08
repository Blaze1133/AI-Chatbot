"use client"

import { useToast } from "@/components/ui/use-toast"
import { motion, AnimatePresence } from "framer-motion"
import { X, CheckCircle2, AlertCircle } from "lucide-react"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <div className="fixed top-6 right-6 z-[100] flex flex-col gap-3 max-w-sm">
      <AnimatePresence>
        {toasts.map(function ({ id, title, description, action, variant, ...props }) {
          return (
            <motion.div
              key={id}
              initial={{ opacity: 0, x: 100, scale: 0.95 }}
              animate={{ opacity: 1, x: 0, scale: 1 }}
              exit={{ opacity: 0, x: 100, scale: 0.95 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className={`group pointer-events-auto relative flex items-start gap-3 p-4 backdrop-blur-xl border rounded-2xl shadow-2xl ${
                variant === "destructive"
                  ? "bg-red-500/10 border-red-500/30 text-red-100"
                  : "bg-white/10 border-white/20 text-white"
              }`}
              {...props}
            >
              {/* Icon */}
              <div className="flex-shrink-0 mt-0.5">
                {variant === "destructive" ? (
                  <AlertCircle className="h-5 w-5 text-red-400" />
                ) : (
                  <CheckCircle2 className="h-5 w-5 text-green-400" />
                )}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                {title && (
                  <div className="text-sm font-semibold mb-1">
                    {title}
                  </div>
                )}
                {description && (
                  <div className="text-sm opacity-90 leading-relaxed">
                    {description}
                  </div>
                )}
              </div>

              {/* Close Button */}
              <button
                onClick={() => {
                  // Manually dismiss the toast
                  const toastElement = document.getElementById(id)
                  if (toastElement) {
                    toastElement.style.opacity = "0"
                    setTimeout(() => {
                      // This will trigger the remove animation
                    }, 300)
                  }
                }}
                className="flex-shrink-0 opacity-60 hover:opacity-100 transition-opacity"
              >
                <X className="h-4 w-4" />
              </button>
            </motion.div>
          )
        })}
      </AnimatePresence>
    </div>
  )
}
