"use client"

import { useState } from "react"
import { Sparkles, Upload, Trash2, Loader2, FileText, User, Bot, Send } from "lucide-react"
import Link from "next/link"

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export default function SimpleChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I'm your AI assistant. Upload a PDF document and ask me anything about it.",
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [documents, setDocuments] = useState<UploadedDocument[]>([])

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append("file", file)

      const response = await fetch(`${API_URL}/api/documents/upload`, {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        setDocuments([...documents, { document_id: result.document_id, filename: result.filename }])
        alert("Document uploaded successfully!")
      } else {
        alert("Upload failed. Please try again.")
      }
    } catch (error) {
      alert("Upload failed. Please try again.")
    } finally {
      setUploading(false)
    }
  }

  const handleDeleteDocument = async (documentId: string) => {
    try {
      const response = await fetch(`${API_URL}/api/documents/${documentId}`, {
        method: "DELETE",
      })

      if (response.ok) {
        setDocuments(documents.filter(doc => doc.document_id !== documentId))
        alert("Document deleted successfully!")
      } else {
        alert("Delete failed. Please try again.")
      }
    } catch (error) {
      alert("Delete failed. Please try again.")
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

    setMessages([...messages, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/chat/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: input,
        }),
      })

      if (response.ok) {
        const result = await response.json()
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: result.answer,
          sources: result.source_documents,
        }
        setMessages(prev => [...prev, assistantMessage])
      } else {
        const errorResponse = await response.json()
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I encountered an error. Please try again.",
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="w-80 bg-black/20 backdrop-blur-xl p-6 border-r border-white/10">
          <div className="mb-8">
            <Link href="/" className="text-2xl font-bold text-white flex items-center gap-2">
              <Sparkles className="w-6 h-6" />
              AI Assistant
            </Link>
          </div>

          {/* Upload Section */}
          <div className="mb-6">
            <h3 className="text-white font-semibold mb-4">Documents</h3>
            <label className="block">
              <div className="border-2 border-dashed border-white/20 rounded-lg p-4 text-center cursor-pointer hover:border-white/40 transition-colors">
                <Upload className="w-8 h-8 mx-auto mb-2 text-white/60" />
                <span className="text-white/60 text-sm">
                  {uploading ? "Uploading..." : "Upload PDF"}
                </span>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileUpload}
                  disabled={uploading}
                  className="hidden"
                />
              </div>
            </label>
          </div>

          {/* Documents List */}
          <div className="space-y-2">
            {documents.map((doc) => (
              <div
                key={doc.document_id}
                className="flex items-center justify-between p-3 bg-white/5 rounded-lg"
              >
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-white/60" />
                  <span className="text-white/80 text-sm truncate">{doc.filename}</span>
                </div>
                <button
                  onClick={() => handleDeleteDocument(doc.document_id)}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-3xl ${
                    message.role === "user"
                      ? "bg-blue-600 text-white"
                      : "bg-white/10 text-white backdrop-blur-sm"
                  } rounded-2xl p-4`}
                >
                  <div className="flex items-start gap-3">
                    {message.role === "assistant" && (
                      <Bot className="w-5 h-5 mt-1 text-blue-400" />
                    )}
                    <div className="flex-1">
                      <p className="whitespace-pre-wrap">{message.content}</p>
                      {message.sources && message.sources.length > 0 && (
                        <div className="mt-3 space-y-2">
                          <p className="text-sm font-semibold text-white/80">Sources:</p>
                          {message.sources.map((source, index) => (
                            <div
                              key={index}
                              className="p-2 bg-white/5 rounded-lg text-sm text-white/60"
                            >
                              <p className="truncate">{source.content}</p>
                              <p className="text-xs mt-1">
                                {source.filename} - Page {source.page}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                    {message.role === "user" && (
                      <User className="w-5 h-5 mt-1 text-blue-200" />
                    )}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4">
                  <div className="flex items-center gap-2 text-white">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div className="border-t border-white/10 p-6">
            <form onSubmit={handleSubmit} className="flex gap-4">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a question about your documents..."
                className="flex-1 bg-white/10 border border-white/20 rounded-full px-6 py-3 text-white placeholder-white/60 focus:outline-none focus:border-white/40"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="bg-blue-600 text-white rounded-full px-6 py-3 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
