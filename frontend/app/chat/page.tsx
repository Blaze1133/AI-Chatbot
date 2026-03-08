"use client"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"
import { Sparkles, Upload, Trash2, Loader2, FileText, User, Bot, Send } from "lucide-react"
import Link from "next/link"
import { useToast } from "@/components/ui/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { motion, AnimatePresence } from "framer-motion"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  sources?: Array<{
    content: string
    page: number
    filename: string
  }>
}

interface UploadedDocument {
  document_id: string
  filename: string
}

const API_URL = "http://localhost:8000"

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI assistant. Upload a PDF document and ask me anything about it.",
    },
  ])
  const [input, setInput] = useState("")
  const [isTyping, setIsTyping] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [documents, setDocuments] = useState<UploadedDocument[]>([])
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const chatContainerRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages, isTyping])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.pdf')) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF file only.",
        variant: "destructive",
      })
      return
    }

    setIsUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_URL}/api/documents/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }))
        throw new Error(errorData.detail || 'Upload failed')
      }

      const data = await response.json()
      setDocuments(prev => [...prev, {
        document_id: data.document_id,
        filename: data.filename
      }])

      toast({
        title: "Success!",
        description: `${data.message} You can now ask questions about this document!`,
      })
    } catch (error) {
      toast({
        title: "Upload failed",
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: "destructive",
      })
      console.error('Upload error:', error)
    } finally {
      setIsUploading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleDeleteDocument = async (docId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/documents/${docId}`, {
        method: 'DELETE',
      })

      if (!response.ok) {
        throw new Error('Delete failed')
      }

      setDocuments(prev => prev.filter(doc => doc.document_id !== docId))
      if (selectedDoc === docId) {
        setSelectedDoc(null)
      }

      toast({
        title: "Success!",
        description: "Document deleted successfully.",
      })
    } catch (error) {
      toast({
        title: "Delete failed",
        description: error instanceof Error ? error.message : 'Unknown error',
        variant: "destructive",
      })
      console.error('Delete error:', error)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsTyping(true)

    try {
      const response = await fetch(`${API_URL}/api/chat/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
          document_id: selectedDoc,
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get answer')
      }

      const data = await response.json()
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        sources: data.source_documents?.map((doc: any) => ({
          content: doc.content,
          page: doc.page,
          filename: doc.filename,
        })),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I couldn't process your question. Make sure you've uploaded a document and the backend is running.",
      }
      setMessages((prev) => [...prev, errorMessage])
      console.error('Question error:', error)
    } finally {
      setIsTyping(false)
    }
  }

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-slate-950 via-purple-950/20 to-slate-950">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 -left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 -right-1/4 w-96 h-96 bg-fuchsia-500/10 rounded-full blur-3xl" />
      </div>

      {/* Left Sidebar - Documents Panel */}
      <aside className="w-80 h-screen p-6 relative z-10">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="h-full bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6 shadow-2xl"
        >
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Documents</h2>
          
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".pdf"
            className="hidden"
          />
          
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="w-full bg-gradient-to-r from-violet-500 to-fuchsia-500 hover:from-violet-600 hover:to-fuchsia-600 text-white font-semibold py-3 rounded-xl shadow-[0_0_15px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(168,85,247,0.6)] transition-all hover:scale-105"
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-5 w-5" />
                Upload PDF
              </>
            )}
          </Button>

          {documents.length === 0 ? (
            <div className="mt-8 border-2 border-dashed border-white/10 rounded-2xl p-8 text-center">
              <FileText className="h-16 w-16 mx-auto mb-4 text-slate-600" />
              <p className="text-slate-400 text-sm">No documents uploaded yet</p>
              <p className="text-slate-500 text-xs mt-2">Upload a PDF to start chatting</p>
            </div>
          ) : (
            <div className="mt-6 space-y-3">
              <h3 className="text-sm font-semibold text-slate-400 mb-3">Recent Documents</h3>
              {documents.map((doc) => (
                <motion.div
                  key={doc.document_id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  onClick={() => setSelectedDoc(doc.document_id)}
                  className={`group cursor-pointer bg-slate-800/50 backdrop-blur-md border border-white/10 rounded-xl p-3 transition-all hover:bg-slate-800/70 ${
                    selectedDoc === doc.document_id ? 'ring-2 ring-violet-500 bg-slate-800/70' : ''
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <FileText className="h-4 w-4 text-violet-400 flex-shrink-0" />
                      <span className="text-sm text-slate-200 truncate">{doc.filename}</span>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        handleDeleteDocument(doc.document_id)
                      }}
                      className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-300 transition-opacity"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {selectedDoc && (
            <div className="mt-6 bg-violet-500/10 border border-violet-500/20 rounded-xl p-3">
              <p className="text-xs text-violet-300 text-center">🎯 Searching in selected document</p>
            </div>
          )}
        </motion.div>
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 h-screen flex flex-col relative z-10">
        {/* Top Navigation */}
        <header className="p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-lg">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-slate-100">AI Assistant</h1>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link href="/">
              <Button variant="ghost" className="text-slate-300 hover:text-slate-100 hover:bg-white/5">← Home</Button>
            </Link>
          </div>
        </header>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto px-6 pb-32" ref={chatContainerRef}>
          <div className="max-w-4xl mx-auto space-y-6">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className={`flex gap-4 ${
                    message.role === "user" ? "flex-row-reverse" : "flex-row"
                  }`}
                >
                  {/* Avatar */}
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.role === "user"
                        ? "bg-gradient-to-br from-violet-500 to-fuchsia-500"
                        : "bg-slate-800/50 backdrop-blur-md border border-white/10"
                    }`}
                  >
                    {message.role === "user" ? (
                      <User className="h-5 w-5 text-white" />
                    ) : (
                      <Bot className="h-5 w-5 text-violet-400" />
                    )}
                  </div>

                  {/* Message Bubble */}
                  <div className="flex-1 max-w-[75%]">
                    <div
                      className={`rounded-2xl p-4 ${
                        message.role === "user"
                          ? "bg-gradient-to-r from-violet-500 to-fuchsia-500 text-white shadow-[0_0_15px_rgba(168,85,247,0.3)]"
                          : "bg-slate-800/50 backdrop-blur-md border border-white/10 text-slate-100"
                      }`}
                    >
                      <p className="leading-relaxed whitespace-pre-wrap">{message.content}</p>
                    </div>

                    {/* Source Citations */}
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-4 space-y-3">
                        <p className="text-xs text-slate-500 font-medium">Sources</p>
                        {message.sources.map((source, idx) => (
                          <div key={idx} className="bg-gradient-to-r from-violet-500/10 to-fuchsia-500/10 backdrop-blur-md border border-violet-500/20 rounded-xl p-4">
                            <div className="flex items-start gap-3">
                              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                                <span className="text-white text-xs font-bold">{idx + 1}</span>
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-slate-200 mb-2">
                                  {source.filename}
                                </p>
                                <p className="text-xs text-violet-400 font-medium mb-2">
                                  Page {source.page}
                                </p>
                                <p className="text-xs text-slate-400 leading-relaxed line-clamp-3">
                                  {source.content}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {/* Typing Indicator */}
            {isTyping && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-4"
              >
                <div className="h-10 w-10 rounded-full bg-slate-800/50 backdrop-blur-md border border-white/10 flex items-center justify-center flex-shrink-0">
                  <Loader2 className="h-5 w-5 text-violet-400 animate-spin" />
                </div>
                <div className="bg-slate-800/50 backdrop-blur-md border border-white/10 rounded-2xl p-4">
                  <div className="flex items-center gap-2 text-slate-400">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">AI is thinking...</span>
                  </div>
                </div>
              </motion.div>
            )}
          </div>
        </div>

        {/* Floating Input Container */}
        <div className="absolute bottom-6 left-6 right-6">
          <div className="max-w-3xl mx-auto">
            <form onSubmit={handleSubmit}>
              <div className="bg-slate-900/60 backdrop-blur-xl border border-white/10 rounded-full shadow-2xl p-2 flex items-center gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask me anything..."
                  className="flex-1 bg-transparent border-none outline-none text-slate-100 placeholder:text-slate-500 px-4 py-2 focus:ring-0"
                />
                <Button
                  type="submit"
                  disabled={!input.trim()}
                  className="h-10 w-10 rounded-full bg-violet-600 hover:bg-fuchsia-600 disabled:bg-slate-700 disabled:text-slate-500 shadow-[0_0_15px_rgba(168,85,247,0.4)] hover:shadow-[0_0_25px_rgba(236,72,153,0.6)] transition-all p-0 flex items-center justify-center"
                >
                  <Send className="h-5 w-5" />
                </Button>
              </div>
            </form>
          </div>
        </div>
      </main>

      <Toaster />
    </div>
  )
}
