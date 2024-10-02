'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Plus, Send, User, Edit2, X, Menu, ChevronLeft, Trash2, MessageSquare } from 'lucide-react'

export function ChatInterfaceComponent() {
  const [chats, setChats] = useState([
    { id: 1, name: 'New Chat', messages: [{ role: 'assistant', content: 'Hello! How can I assist you today?' }] }
  ])
  const [currentChatId, setCurrentChatId] = useState(1)
  const [inputMessage, setInputMessage] = useState('')
  const [newChatName, setNewChatName] = useState('')
  const [isNaming, setIsNaming] = useState(false)
  const [editingChatId, setEditingChatId] = useState<number | null>(null)
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const editInputRef = useRef<HTMLInputElement>(null)

  const currentChat = chats.find(chat => chat.id === currentChatId) || chats[0]

  useEffect(() => {
    if (editingChatId !== null && editInputRef.current) {
      editInputRef.current.focus()
    }
  }, [editingChatId])

  const handleNewChat = () => {
    setIsNaming(true)
    setNewChatName('')
  }

  const createNewChat = () => {
    const newChatId = chats.length + 1
    const chatName = newChatName.trim() || `New Chat ${newChatId}`
    setChats([...chats, { id: newChatId, name: chatName, messages: [{ role: 'assistant', content: 'Hello! How can I assist you today?' }] }])
    setCurrentChatId(newChatId)
    setInputMessage('')
    setIsNaming(false)
  }

  const cancelNewChat = () => {
    setIsNaming(false)
    setNewChatName('')
  }

  const handleEditChat = (chatId: number) => {
    setEditingChatId(chatId)
  }

  const saveEditedChatName = (chatId: number, newName: string) => {
    setChats(chats.map(chat => 
      chat.id === chatId ? { ...chat, name: newName.trim() || chat.name } : chat
    ))
    setEditingChatId(null)
  }

  const handleDeleteChat = (chatId: number) => {
    const updatedChats = chats.filter(chat => chat.id !== chatId)
    setChats(updatedChats)
    if (chatId === currentChatId) {
      setCurrentChatId(updatedChats[0]?.id || 0)
    }
  }

  const handleSendMessage = () => {
    if (inputMessage.trim() !== '') {
      const updatedChats = chats.map(chat => {
        if (chat.id === currentChatId) {
          return {
            ...chat,
            messages: [...chat.messages, { role: 'user', content: inputMessage }]
          }
        }
        return chat
      })
      setChats(updatedChats)
      setInputMessage('')
      
      // Simulate AI response
      setTimeout(() => {
        const updatedChatsWithAIResponse = updatedChats.map(chat => {
          if (chat.id === currentChatId) {
            return {
              ...chat,
              messages: [...chat.messages, { role: 'assistant', content: 'This is a simulated AI response.' }]
            }
          }
          return chat
        })
        setChats(updatedChatsWithAIResponse)
      }, 1000)
    }
  }

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen)
  }

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-900 to-black text-gray-300">
      {/* Sidebar */}
      <div className={`${isSidebarOpen ? 'w-80' : 'w-0'} bg-black bg-opacity-50 backdrop-blur-lg transition-all duration-300 ease-in-out overflow-hidden border-r border-purple-900`}>
        <div className="p-4">
          {isNaming ? (
            <div className="flex flex-col mb-4">
              <div className="flex mb-2">
                <Input
                  className="flex-1 bg-gray-800 border-gray-700 text-gray-300 focus:ring-purple-500 focus:border-purple-500 rounded-l-full"
                  placeholder="Enter chat name"
                  value={newChatName}
                  onChange={(e) => setNewChatName(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && createNewChat()}
                />
                <Button className="rounded-r-full bg-purple-600 hover:bg-purple-700" onClick={createNewChat}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
              <Button 
                variant="ghost" 
                className="self-start text-gray-400 hover:text-gray-300"
                onClick={cancelNewChat}
              >
                <X className="h-4 w-4 mr-2" /> Cancel
              </Button>
            </div>
          ) : (
            <Button className="w-full mb-4 bg-purple-600 hover:bg-purple-700 transition-colors duration-200 rounded-full" onClick={handleNewChat}>
              <Plus className="mr-2 h-4 w-4" /> New Chat
            </Button>
          )}
          <ScrollArea className="h-[calc(100vh-5rem)]">
            <div className="space-y-2">
              {chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`flex items-center justify-between truncate text-sm ${chat.id === currentChatId ? 'bg-purple-900 bg-opacity-50' : 'hover:bg-purple-900 hover:bg-opacity-30'} rounded-lg p-3 cursor-pointer transition-all duration-200 transform hover:scale-105`}
                  onClick={() => setCurrentChatId(chat.id)}
                >
                  {editingChatId === chat.id ? (
                    <Input
                      ref={editInputRef}
                      className="flex-1 bg-gray-800 border-gray-700 text-gray-300 focus:ring-purple-500 focus:border-purple-500 rounded-full"
                      defaultValue={chat.name}
                      onBlur={(e) => saveEditedChatName(chat.id, e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && saveEditedChatName(chat.id, e.currentTarget.value)}
                    />
                  ) : (
                    <>
                      <span className="flex-1 flex items-center">
                        <MessageSquare className="h-4 w-4 mr-2 text-purple-400" />
                        {chat.name}
                      </span>
                      <div className="flex">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="ml-2 text-gray-400 hover:text-gray-300 transition-colors duration-200"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleEditChat(chat.id)
                          }}
                        >
                          <Edit2 className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="ml-2 text-gray-400 hover:text-red-500 transition-colors duration-200"
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteChat(chat.id)
                          }}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="bg-black bg-opacity-50 backdrop-blur-lg p-4 flex items-center border-b border-purple-900">
          <Button variant="ghost" onClick={toggleSidebar} className="mr-4 text-gray-400 hover:text-gray-300 transition-colors duration-200">
            {isSidebarOpen ? <ChevronLeft className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </Button>
          <h1 className="text-xl font-semibold text-purple-300">{currentChat.name}</h1>
        </div>

        <ScrollArea className="flex-1 p-6">
          {currentChat.messages.map((message, index) => (
            <div key={index} className={`flex items-start mb-6 ${message.role === 'user' ? 'justify-end' : ''}`}>
              {message.role === 'assistant' && (
                <div className="bg-purple-600 rounded-full p-2 mr-3 shadow-lg">
                  <User className="h-6 w-6" />
                </div>
              )}
              <div className={`rounded-2xl p-4 max-w-[70%] ${message.role === 'user' ? 'bg-purple-600' : 'bg-gray-800 bg-opacity-75'} shadow-lg backdrop-blur-sm transition-all duration-200 hover:scale-105`}>
                {message.content}
              </div>
            </div>
          ))}
        </ScrollArea>

        {/* Input Area */}
        <div className="p-4 border-t border-purple-900 bg-black bg-opacity-50 backdrop-blur-lg">
          <div className="flex items-center max-w-4xl mx-auto">
            <Input
              className="flex-1 bg-gray-800 border-gray-700 text-gray-300 rounded-l-full focus:ring-purple-500 focus:border-purple-500"
              placeholder="Type your message here..."
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            />
            <Button className="rounded-r-full bg-purple-600 hover:bg-purple-700 transition-all duration-200 transform hover:scale-105" onClick={handleSendMessage}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}